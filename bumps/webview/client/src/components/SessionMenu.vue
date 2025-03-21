<script setup lang="ts">
import DropDown from "./DropDown.vue";
import {
  active_fit,
  autosave_session,
  autosave_session_interval,
  fileBrowser,
  session_output_file,
} from "../app_state";
import type { FileBrowserSettings } from "../app_state";
import type { AsyncSocket } from "../asyncSocket";

// const title = "Session";
const props = defineProps<{
  socket: AsyncSocket;
}>();

function handle_file_message(payload: { filename: string; pathlist: string[] }) {
  console.log("session_output_file", payload);
  session_output_file.value = payload;
}

function handle_autosave_message(payload: boolean) {
  console.log("autosave_session", payload);
  autosave_session.value = payload;
}

function handle_autosave_interval_message(payload: number) {
  console.log("autosave_session_interval", payload);
  autosave_session_interval.value = payload;
}

props.socket.asyncEmit("get_shared_setting", "session_output_file", handle_file_message);
props.socket.asyncEmit("get_shared_setting", "autosave_session", handle_autosave_message);
props.socket.asyncEmit("get_shared_setting", "autosave_session_interval", handle_autosave_interval_message);
props.socket.on("session_output_file", handle_file_message);
props.socket.on("autosave_session", handle_autosave_message);
props.socket.on("autosave_session_interval", handle_autosave_interval_message);

async function toggle_autosave() {
  // if turning on autosave, but session_file is not set, then prompt for a file
  if (!autosave_session.value && !session_output_file.value) {
    // open the file browser to select output file, and then set autosave
    await setOutputFile(true, false);
    // closeMenu();
    return;
  }
  await props.socket.asyncEmit("set_shared_setting", "autosave_session", !autosave_session.value);
  // setTimeout(closeMenu, 1000);
}

async function set_interval(new_interval: number) {
  await props.socket.asyncEmit("set_shared_setting", "autosave_session_interval", new_interval);
  closeMenu();
}

async function saveSession() {
  if (session_output_file.value) {
    await props.socket.asyncEmit("save_session");
  } else {
    await setOutputFile(false, true);
  }
}

function closeMenu() {
  const menu = document.getElementById("session-dropdown-menu");
  if (menu) {
    menu.classList.remove("show");
  }
}

async function readSession(readOnly: boolean) {
  if (active_fit.value && active_fit.value?.fitter_id) {
    const confirmation = confirm("Loading session will stop current fit. Continue?");
    if (!confirmation) {
      return;
    }
  }
  if (fileBrowser.value) {
    const settings: FileBrowserSettings = {
      title: "Read Session",
      callback: async (pathlist, filename) => {
        props.socket.asyncEmit("load_session", pathlist, filename, readOnly);
      },
      show_name_input: true,
      name_input_label: "Session Filename",
      require_name: true,
      show_files: true,
      search_patterns: [".h5"],
      chosenfile_in: "",
      pathlist_in: session_output_file.value?.pathlist,
    };
    fileBrowser.value.open(settings);
  }
}

async function saveSessionCopy() {
  if (fileBrowser.value) {
    const settings: FileBrowserSettings = {
      title: "Save Session (Copy)",
      callback: async (pathlist, filename) => {
        await props.socket.asyncEmit("save_session_copy", pathlist, filename);
      },
      show_name_input: true,
      name_input_label: "Filename",
      require_name: true,
      show_files: true,
      search_patterns: [".h5"],
      chosenfile_in: "",
      pathlist_in: session_output_file.value?.pathlist,
    };
    fileBrowser.value.open(settings);
  }
}

async function setOutputFile(enable_autosave = true, immediate_save = false) {
  if (fileBrowser.value) {
    const settings: FileBrowserSettings = {
      title: "Set Output File",
      callback: async (pathlist, filename) => {
        let input = filename;
        if (input.includes("/")) {
          alert("FileBrowser: '/' in filename not yet supported");
          return;
        }
        if (!input.endsWith(".h5") && !input.endsWith(".hdf5")) {
          filename = `${filename}.session.h5`;
        }
        await props.socket.asyncEmit("set_shared_setting", "session_output_file", { filename, pathlist });
        if (enable_autosave) {
          await props.socket.asyncEmit("set_shared_setting", "autosave_session", true);
        }
        if (immediate_save) {
          await props.socket.asyncEmit("save_session");
        }
      },
      show_name_input: true,
      name_input_label: "Output Filename",
      require_name: true,
      show_files: true,
      search_patterns: [".h5"],
      chosenfile_in: session_output_file.value?.filename,
      pathlist_in: session_output_file.value?.pathlist,
    };
    fileBrowser.value.open(settings);
  }
}

async function unsetOutputFile() {
  await props.socket.asyncEmit("set_shared_setting", "session_output_file", null);
}
</script>

<template>
  <DropDown v-slot="{ hide }" title="Session">
    <li class="dropdown-item">
      <div class="form-check form-switch">
        <label class="form-check-label" for="autoSaveSessionCheckbox">Autosave</label>
        <input
          id="autoSaveSessionCheckbox"
          class="form-check-input"
          type="checkbox"
          role="switch"
          :checked="autosave_session"
          @change="toggle_autosave"
        />
      </div>
    </li>
    <li>
      <span v-if="session_output_file" class="">
        <span class="dropdown-item-text">{{ session_output_file.filename }}</span>
      </span>
    </li>
    <li class="dropdown-item">
      <div class="row">
        <label for="autosaveIntervalInput" class="col col-form-label col-form-label-sm">Interval (s)</label>
        <div class="col-auto">
          <input
            id="autosaveIntervalInput"
            type="number"
            class="form-control form-control"
            :value="autosave_session_interval"
            @change="set_interval(($event.target as HTMLInputElement).valueAsNumber)"
          />
        </div>
      </div>
    </li>
    <li>
      <hr class="dropdown-divider" />
    </li>
    <li>
      <button
        class="btn btn-link dropdown-item"
        :class="{ disabled: active_fit?.fitter_id }"
        @click="
          readSession(false);
          hide();
        "
      >
        Open Session
      </button>
    </li>
    <li>
      <button
        class="btn btn-link dropdown-item"
        @click="
          saveSession();
          hide();
        "
      >
        Save Session
      </button>
    </li>
    <li>
      <button
        class="btn btn-link dropdown-item"
        @click="
          setOutputFile(false, true);
          hide();
        "
      >
        Save Session As
      </button>
    </li>
  </DropDown>
</template>
