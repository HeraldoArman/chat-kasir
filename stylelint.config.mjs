/** @type {import('stylelint').Config} */
const config = {
  extends: ["ultracite/stylelint"],
  rules: {
    "import-notation": null,
    "at-rule-no-unknown": [
      true,
      {
        ignoreAtRules: [
          "tailwind",
          "apply",
          "layer",
          "variants",
          "responsive",
          "screen",
          "source",
          "reference",
          "theme",
          "custom-variant",
        ],
      },
    ],
    "at-rule-empty-line-before": null,
    "rule-empty-line-before": null,
    "lightness-notation": null,
    "hue-degree-notation": null,
    "declaration-property-value-no-unknown": null,
  },
};

export default config;
