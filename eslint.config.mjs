import js from "@eslint/js";
import globals from "globals";
import prettierPlugin from "eslint-plugin-prettier";
import reactPlugin from "eslint-plugin-react";
import reactHooksPlugin from "eslint-plugin-react-hooks";
import babelParser from "@babel/eslint-parser";

export default [
  // Node backend
  {
    files: ["apps/backend/**/*.js", "apps/backend/**/*.mjs"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: {
        ...globals.node
      }
    },
    rules: {
      "no-unused-vars": ["warn", { argsIgnorePattern: "^_" }],
      "no-console": "off",
      eqeqeq: ["error", "always"],
      "no-var": "error",
      "prefer-const": "error",
      curly: ["error", "all"]
    }
  },

  // React frontend
  {
    files: ["apps/frontend/**/*.js", "apps/frontend/**/*.jsx"],
    languageOptions: {
      parser: babelParser,
      parserOptions: {
        requireConfigFile: false,
        ecmaVersion: "latest",
        sourceType: "module",
        ecmaFeatures: { jsx: true },
        babelOptions: {
          presets: ["@babel/preset-react"] // ✅ crucial
        }
      },
      globals: {
        React: "readonly"
      }
    },
    plugins: {
      prettier: prettierPlugin,
      react: reactPlugin,
      "react-hooks": reactHooksPlugin
    },
    rules: {
      "prettier/prettier": "error",
      "react/react-in-jsx-scope": "off",
      "react-hooks/rules-of-hooks": "error",
      "react-hooks/exhaustive-deps": "warn",

      "no-unused-vars": ["warn", { argsIgnorePattern: "^_" }],
      "no-console": "off",
      eqeqeq: ["error", "always"],
      "no-var": "error",
      "prefer-const": "error",
      curly: ["error", "all"]
    }
  }
];
