<template>
  <v-app>
    <NavBar />

    <v-content>
      <router-view :key="$route.fullPath" />
    </v-content>
  </v-app>
</template>

<script>
import NavBar from "@/components/NavBar";

export default {
  name: "App",

  components: {
    NavBar
  }
};
</script>

<style>
a {
  text-decoration: none;
}
</style>
