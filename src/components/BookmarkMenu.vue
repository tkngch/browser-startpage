<!-- Menu for bookmarks (e.g., adding, filtering, and sorting) -->
<template>
  <v-list dense rounded max-width="300">
    <v-list-item>
      <v-card>
        <v-expansion-panels multiple hover>
          <!-- Create a new bookmark -->
          <v-expansion-panel>
            <v-expansion-panel-header ripple>
              <span>
                <v-icon>mdi-bookmark-plus</v-icon>
                Create
              </span>
            </v-expansion-panel-header>
            <v-expansion-panel-content>
              <v-form v-on:submit="createBookmark" @submit.prevent>
                <v-text-field
                  label="URL"
                  clearable
                  autofocus
                  v-model="newBookmarkURL"
                >
                </v-text-field>
                <v-btn type="submit">
                  Submit
                </v-btn>
              </v-form>
            </v-expansion-panel-content>
          </v-expansion-panel>
          <!-- END: Create a new bookmark -->

          <!-- Filter -->
          <v-expansion-panel>
            <v-expansion-panel-header ripple>
              <span>
                <v-icon>mdi-filter</v-icon>
                Filter
              </span>
            </v-expansion-panel-header>
            <v-expansion-panel-content>
              <!-- By Tags -->
              By Tags
              <v-chip-group v-model="filterBy.tags" column multiple>
                <v-chip
                  filter
                  outlined
                  v-for="tag in allTags"
                  :key="tag"
                  :value="tag"
                >
                  {{ tag }}
                </v-chip>
              </v-chip-group>
              <!-- By Status -->
              By Status
              <v-chip-group v-model="filterBy.statusCodes" column multiple>
                <v-chip
                  filter
                  outlined
                  v-for="code in allStatusCodes"
                  :key="code"
                  :value="code"
                >
                  {{ code }}
                </v-chip>
              </v-chip-group>
            </v-expansion-panel-content>
          </v-expansion-panel>
          <!-- END: Filter -->

          <!-- Sort -->
          <v-expansion-panel>
            <v-expansion-panel-header ripple>
              <span>
                <v-icon>mdi-sort</v-icon>
                Sort
              </span>
            </v-expansion-panel-header>
            <v-expansion-panel-content>
              <v-chip-group v-model="sortBy" column>
                <v-chip
                  filter
                  outlined
                  v-for="option in sortOptions"
                  :key="option"
                  :value="option"
                >
                  {{ option }}
                </v-chip>
              </v-chip-group>
            </v-expansion-panel-content>
          </v-expansion-panel>
          <!-- END: Sort -->
        </v-expansion-panels>
      </v-card>
    </v-list-item>
  </v-list>
</template>

<script>
export default {
  props: ["allTags", "allStatusCodes", "sortOptions"],

  data: function() {
    return {
      newBookmarkURL: "",
      sortBy: null,
      filterBy: { tags: [], statusCodes: [] }
    };
  },

  methods: {
    createBookmark() {
      if (this.newBookmarkURL.length > 0) {
        this.$emit("create-bookmark", this.newBookmarkURL);
      }
      this.newBookmarkURL = "";
    }
  },

  watch: {
    "filterBy.tags": function(newFilter) {
      this.$emit("filter-bookmarks", {
        tags: newFilter,
        statusCodes: this.filterBy.statusCodes
      });
    },

    "filterBy.statusCodes": function(newFilter) {
      this.$emit("filter-bookmarks", {
        tags: this.filterBy.tags,
        statusCodes: newFilter
      });
    },

    sortBy: function(newSortBy) {
      this.$emit("sort-bookmarks", newSortBy);
    }
  }
};
</script>
