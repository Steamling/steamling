# Translating Steamling Control

Every string the panel shows goes through `t()` (see `../i18n.ts`) with its English text, for
example `t("Performance Overlay")`. A translation is a map from that English text to yours.

To add a language:

1. Create `xx.ts` here (`xx` is the two-letter language code, like `de` or `es`):

   ```ts
   export default {
     "Performance Overlay": "Leistungsanzeige",
     "Cleared {size}": "{size} gelöscht",
   } as Record<string, string>;
   ```

   Keep `{placeholders}` as they are; the panel fills them in.
2. Register it in `index.ts`: `import de from "./de";` and add `de` to `catalogs`.
3. Rebuild the plugin (`npm run build`). Anything you leave out stays in English.

The language follows Steam's own language setting.
