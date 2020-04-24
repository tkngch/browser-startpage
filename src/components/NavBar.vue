<template>
  <v-app-bar app>
    <v-btn text color="primary" to="/">
      <v-icon>mdi-home</v-icon>
      Home
    </v-btn>

    <v-btn text color="primary" to="/bookmarks">
      <v-icon>mdi-book</v-icon>
      Bookmarks
    </v-btn>
  </v-app-bar>
</template>

<style scoped>
a {
  text-decoration: none;
}
</style>
