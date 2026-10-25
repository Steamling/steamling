import { gamepadTabbedPageClasses } from "@decky/ui";

// The panel fills whatever width the quick access menu has. It used to be pinned to the Deck's
// 316px with position: fixed, which broke on screens where Steam lays the menu out at another
// scale (the RP6: oversized text, controls cut off). Armada fixed the same container this way.
export const styles = `
      .steamling-control-tabs {
        width: 100%;
        height: 95vh;
        min-width: 0;
        min-height: 0;
      }
      .steamling-control-tabs > div {
        height: 100%;
        min-height: 0;
      }
      .steamling-control-tabs > div > div:first-child::before {
        background: #0D141C;
        box-shadow: none;
        backdrop-filter: none;
      }
      .steamling-control-tabs .${gamepadTabbedPageClasses.TabContents},
      .steamling-control-tabs .${gamepadTabbedPageClasses.TabContentsScroll},
      .steamling-control-tabs .steamling-control-tab-content {
        min-width: 0;
      }
      .steamling-control-tabs .${gamepadTabbedPageClasses.TabContentsScroll} {
        padding-left: 0;
        padding-right: 0;
      }
      .steamling-control-tabs [role="tablist"] {
        display: flex;
        flex-wrap: nowrap;
        justify-content: center;
      }
      .steamling-control-tabs [role="tab"] {
        flex: 0 1 auto;
        min-width: 0;
        box-sizing: border-box;
        padding-left: 6px;
        padding-right: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      .steamling-control-tabs [role="tab"] svg {
        display: block;
        margin: 0;
      }
      .steamling-control-tabs .steamling-control-tab-content {
        padding-bottom: 24px;
      }
      .steamling-control-tabs .steamling-log {
        font-family: monospace;
        font-size: 10px;
        line-height: 14px;
        word-break: break-all;
        white-space: pre-wrap;
      }
      .steamling-control-tabs .steamling-note {
        box-sizing: border-box;
        width: 100%;
        padding: 8px 16px 8px;
        font-size: 12px;
        line-height: 16px;
        opacity: 0.62;
        text-align: left;
        justify-content: flex-start;
        align-self: stretch;
      }
    `;
