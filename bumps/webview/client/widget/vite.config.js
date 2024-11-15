// vite.config.js
import { defineConfig } from "vite";
import vue from '@vitejs/plugin-vue';

export default defineConfig({
    plugins: [vue()],
    define: {
      'process.env.NODE_ENV': "'production'",
    },
	build: {
		outDir: "src/widget/static",
		lib: {
			entry: ["js/widget.ts"],
			formats: ["es"],
		},
	},
});
