import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";

const embeddedData =
  /<script type="application\/json" id="learning-artifact">([\s\S]*?)<\/script>/;
const externalScript = /<script\s+src=/;
const privateImport = /@repo\//;
const placeholders = /\{\w+\}/g;
const root = new URL("../", import.meta.url);
const read = (path) => readFileSync(new URL(path, root), "utf8");
const manifest = JSON.parse(read("manifest.json"));
test("version and the existing course dependency", () => {
  assert.equal(JSON.parse(read("package.json")).version, manifest.version);
  assert.equal(manifest.references[0].resourceId, "opendesign.html-ppt");
});
for (const item of manifest.templates) {
  test(item.id, () => {
    const sample = JSON.parse(read(item.example));
    const ajv = new Ajv2020({ strict: false });
    addFormats(ajv);
    const validate = ajv.compile(JSON.parse(read(item.schema)));
    assert.ok(validate(sample), JSON.stringify(validate.errors));
    assert.equal(sample.module, item.module);
    assert.ok(read(item.instructions).includes("schema.json"));
    const html = read(item.preview);
    const content = html.match(embeddedData);
    assert.deepEqual(JSON.parse(content[1]), sample);
    assert.doesNotMatch(html, externalScript);
    assert.doesNotMatch(read(item.entry), privateImport);
  });
}
test("translated controls share keys and interpolation parameters", () => {
  const en = JSON.parse(read("locales/en.json"));
  for (const code of ["zh", "de", "es", "fr", "it", "ja", "pt"]) {
    const dict = JSON.parse(read(`locales/${code}.json`));
    assert.deepEqual(Object.keys(dict).sort(), Object.keys(en).sort());
    for (const [key, label] of Object.entries(dict)) {
      const parameters = (text) => (text.match(placeholders) ?? []).sort();
      assert.deepEqual(parameters(label), parameters(en[key]));
    }
  }
});
