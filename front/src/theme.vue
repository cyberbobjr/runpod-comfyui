<script setup>
import { NConfigProvider } from "naive-ui";
import App from "./App.vue";

const themeOverrides = {
  common: {
    primaryColor: "#df691a",
    primaryColorHover: "#e98b39",
    primaryColorPressed: "#c65a11",
    primaryColorSuppl: "#f0ad4e",
    textColorBase: "#ffffff",
    bodyColor: "#0f2537",
    cardColor: "#142d42",
    modalColor: "#142d42",
    popoverColor: "#1c3a50",
    tableColor: "#142d42",
    dividerColor: "#3b4c5a",
    borderColor: "#3b4c5a",
    placeholderColor: "#aab2bd",
    inputColor: "#1a3246",
    actionColor: "#1a3246",
    tableHeaderColor: "#1f3c51",
    tableBorderColor: "#3b4c5a",
    scrollbarColor: "#3b4c5a",
    scrollbarColorHover: "#5bc0de",
  },
  Button: {
    // PRIMARY (orange) – reste inchangé
    textColor: "#ffffff",
    color: "#df691a",
    colorHover: "#e98b39",
    colorPressed: "#c65a11",
    colorFocus: "#e98b39",
    rippleColor: "#df691a",
    border: "1px solid #df691a",

    // DEFAULT (gris personnalisé)
    // 🟡 Ajoute ceci :
    colorSecondary: "#4e5d6c",
    colorSecondaryHover: "#5f7080",
    colorSecondaryPressed: "#3d4b59",
    colorSecondaryFocus: "#5f7080",
    borderSecondary: "1px solid #3b4c5a",
    textColorSecondary: "#ffffff",
    rippleColorSecondary: "#4e5d6c",
  },
  Input: {
    color: "#1a3246",
    textColor: "#ffffff",
    placeholderColor: "#aab2bd",
    border: "1px solid #3b4c5a",
  },
  Select: {
    peers: {
      InternalSelection: {
        color: "#1a3246",
        textColor: "#ffffff",
        placeholderColor: "#aab2bd",
        border: "1px solid #3b4c5a",
      },
      InternalSelectMenu: {
        color: "#1a3246",
        textColor: "#ffffff",
      },
    },
  },
  Card: {
    color: "#142d42",
    textColor: "#ffffff",
    border: "1px solid #3b4c5a",
    titleTextColor: "#df691a",
  },
  Modal: {
    color: "#142d42",
    textColor: "#ffffff",
    border: "1px solid #3b4c5a",
  },
  DataTable: {
    headerColor: "#1f3c51",
    headerTextColor: "#ffffff",
    rowColor: "#142d42",
    rowTextColor: "#ffffff",
    borderColor: "#3b4c5a",
  },
  Pagination: {
    itemTextColor: "#ffffff",
    itemTextColorActive: "#df691a",
    itemColorActive: "#1c2a36",
  },
  Form: {
    labelTextColor: "#ffffff", // ✅ Ajoute ceci
  },
  FormItem: {
    labelTextColor: "#ffffff", // ✅ Optionnel, selon le composant utilisé
  },
  Typography: {
    titleTextColor: "#df691a", // ou themeOverrides.common.primaryColor
  },
};
</script>

<template>
  <n-config-provider :theme-overrides="themeOverrides">
    <App />
  </n-config-provider>
</template>
