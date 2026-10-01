// Test motorlarının sürümlerini yazar (kanıt raporu için).
import { chromium, firefox, webkit } from "@playwright/test";
const out = {};
for (const [name, type] of [["chromium", chromium], ["firefox", firefox], ["webkit", webkit]]) {
  const b = await type.launch();
  out[name] = b.version();
  await b.close();
}
console.log(JSON.stringify(out));
