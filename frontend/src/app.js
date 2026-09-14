import Alpine from "alpinejs";
import focus from "@alpinejs/focus";
import htmx from "htmx.org";
import {createIcons, icons} from "lucide";

window.Alpine = Alpine;
window.htmx = htmx;
Alpine.plugin(focus);
Alpine.start();

const refreshIcons = () => createIcons({icons});
document.addEventListener("DOMContentLoaded", refreshIcons);
document.body.addEventListener("htmx:afterSwap", refreshIcons);
