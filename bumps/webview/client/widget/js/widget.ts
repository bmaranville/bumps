import { createApp } from 'vue/dist/vue.esm-bundler.js';
import type { AnyModel, RenderProps } from "@anywidget/types";
import "./widget.css";
import 'bootstrap/dist/css/bootstrap.min.css';
import '../../src/style.css';
import { panels } from "../../src/panels.mjs";
import App from "../../src/App.vue";
import SummaryView from "../../src/components/SummaryView.vue";
import { ca } from 'date-fns/locale';

class SocketAdapter {
  model: AnyModel<WidgetModel>;
  invoke: Function;
  callbacks: any = {};
  constructor(model: AnyModel<WidgetModel>, invoke: Function) {
	this.model = model;
	this.invoke = invoke;
	this.callbacks = {};
	// console.log(this.asyncEmit("custom", "hello"));
	console.log("SocketAdapter created", model);
	// this.model.on("msg:custom", (msg) => {
	// 	console.log("msg:custom", msg);
	// });
	this.model.on("msg:custom", this.handle_message.bind(this));
  }
  async connect(sid: string) {
    console.log('connecting!', sid);
  }
  async asyncEmit(message: string, ...payload) {
    // console.log('received asyncEmit: ', message, payload);
	let callback = null;
	if (payload.length > 0 && typeof payload[payload.length - 1] === "function") {
		callback = payload.pop();
	}
	const [result, buffers] = await this.invoke("_asyncEmit", {message, payload});
	if (callback !== null) {
		await callback(result);
	}

	// console.log("result", result);
	return result;
  }
  handle_message(msg: any, buffers: any) {
	// console.log('received message!', msg, buffers);
	if (msg.type === "emit") {
		// console.log("emit", msg, this.callbacks);
		for (const callback of this.callbacks[msg.topic] ?? []) {
			// console.log("calling callback", callback, msg.message);
			callback(msg.message);
		}
	}
	if (msg.kind === "anywidget-command-response") {
		return
	}
	
  }
  on(topic: string, callback: Function) {
	// console.log("on", topic, callback);
	if (!(topic in this.callbacks)) {
		this.callbacks[topic] = [];
	}
	this.callbacks[topic].push(callback);
	if (topic === "connect") {
		callback();
	}
  }
  off(topic: string, callback: Function) {
	if (topic in this.callbacks) {
		this.callbacks[topic] = this.callbacks[topic].filter((cb: Function) => cb !== callback);
	}
  }
}


/* Specifies attributes defined with traitlets in ../src/widget/__init__.py */
interface WidgetModel {
	value: number;
	/* Add your own */
}

function original_render({ model, e, experimental }: RenderProps<WidgetModel>) {
	let btn = document.createElement("button");
	btn.innerHTML = `count is ${model.get("value")}`;
	btn.addEventListener("click", () => {
		model.set("value", model.get("value") + 1);
		model.save_changes();
	});
	model.on("change:value", () => {
		btn.innerHTML = `count is ${model.get("value")}`;
	});
	el.classList.add("widget");
	el.appendChild(btn);
}

function render({model, el, experimental}: RenderProps<WidgetModel>) {
  const socket = new SocketAdapter(model, experimental.invoke);
  const app = createApp(App, {panels, socket, single_panel: null}).mount(el);
}

export default { render };
