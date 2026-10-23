/**
 * matt-pocock-skills — self-registering OpenCode plugin.
 *
 * Registers every skill vendored from the `mattpocock/skills` git submodule
 * (skills/matt-pocock-skills) as OpenCode skills, so they are advertised and
 * loadable the same way as native skills — no symlinks or per-skill config.
 *
 * Why a plugin instead of the `skills` config array: mattpocock/skills nests
 * its skills two levels deep (skills/<category>/<name>/SKILL.md). This plugin
 * walks that layout and injects each skill via `ctx.skill.transform`.
 *
 * Self-contained on purpose: the default export is a plain plugin object, so
 * there is no `@opencode/plugin` import to resolve from this repo location.
 * `Plugin.define` in @opencode/plugin is an identity function, so the plain
 * object is exactly what the loader expects: { id, setup(ctx) }.
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Plugin lives at <repo>/.opencode/plugins/matt-pocock-skills/index.js
// Matt's skills live at   <repo>/skills/matt-pocock-skills/skills
const SKILLS_ROOT = path.resolve(__dirname, "../../../skills/matt-pocock-skills/skills");

// Top-level categories to leave unregistered. Edit to taste.
const SKIP_CATEGORIES = new Set(["deprecated", "in-progress"]);

const MAX_DEPTH = 6;

// Find every leaf SKILL.md. A directory that directly contains SKILL.md is one
// skill; we do not descend into it (its subdirs are supporting files).
function walkSkillMd(dir, out, depth) {
  if (depth > MAX_DEPTH) return;
  let entries;
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true });
  } catch {
    return;
  }
  if (entries.some((e) => e.isFile() && e.name === "SKILL.md")) {
    out.push(path.join(dir, "SKILL.md"));
    return;
  }
  for (const e of entries) {
    if (e.name.startsWith(".") || e.name === "node_modules") continue;
    if (e.isDirectory()) walkSkillMd(path.join(dir, e.name), out, depth + 1);
  }
}

function collectSkillFiles() {
  const out = [];
  let categories;
  try {
    categories = fs.readdirSync(SKILLS_ROOT, { withFileTypes: true });
  } catch {
    return out;
  }
  for (const cat of categories) {
    if (!cat.isDirectory() || cat.name.startsWith(".")) continue;
    if (SKIP_CATEGORIES.has(cat.name)) continue;
    walkSkillMd(path.join(SKILLS_ROOT, cat.name), out, 0);
  }
  return out;
}

// Minimal frontmatter reader: pulls single-line `name:` / `description:` and
// returns the body with frontmatter stripped. Matches the pragmatic parsing
// used by the sibling superpowers plugin.
function parseFrontmatter(text) {
  const match = text.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/);
  if (!match) return { data: {}, body: text };
  const [, raw, body] = match;
  const data = {};
  for (const line of raw.split(/\r?\n/)) {
    const idx = line.indexOf(":");
    if (idx <= 0) continue;
    const key = line.slice(0, idx).trim();
    const value = line
      .slice(idx + 1)
      .trim()
      .replace(/^["']|["']$/g, "");
    if (key && !(key in data)) data[key] = value;
  }
  return { data, body };
}

export default {
  id: "matt-pocock-skills",
  async setup(ctx) {
    const files = collectSkillFiles();
    if (files.length === 0) return;

    // Respect existing skills: never clobber the user's own or another
    // source's skill that already owns an id.
    const existing = new Set();
    try {
      for (const s of await ctx.skill.list()) existing.add(s.id);
    } catch {
      /* listing may be unavailable this early; the transform guard still applies */
    }

    const skills = [];
    const seen = new Set();
    for (const file of files) {
      const id = path.basename(path.dirname(file));
      if (seen.has(id) || existing.has(id)) continue;
      let text;
      try {
        text = fs.readFileSync(file, "utf8");
      } catch {
        continue;
      }
      const { data, body } = parseFrontmatter(text);
      // OpenCode only advertises skills that have a description.
      if (!data.description) continue;
      seen.add(id);
      const skill = {
        id,
        name: data.name || id,
        description: data.description,
        path: file,
        content: body.trim(),
      };
      // Honor Matt's user-invoked marker: keep it loadable by id, but hide it
      // from the model's auto-invoke list (same intent as opencode/autoinvoke).
      if (/^true$/i.test(data["disable-model-invocation"] || "")) {
        skill.autoinvoke = false;
      }
      skills.push(skill);
    }

    if (skills.length === 0) return;

    await ctx.skill.transform((editor) => {
      for (const skill of skills) {
        if (editor.get(skill.id)) continue;
        editor.add(skill);
      }
    });
  },
};
