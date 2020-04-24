<!-- Editing card for single bookmark entry -->
<template>
  <v-card class="mx-auto" max-width="400">
    <v-card-title>
      {{ bookmark.title }}
    </v-card-title>
    <v-card-subtitle>
      {{ bookmark.url }}
    </v-card-subtitle>
    <!-- Card content -->
    <v-card-text>
      <!-- Editing -->
      <v-text-field
        label="Edit description"
        v-model="edited.description"
        outlined
      >
      </v-text-field>
      <v-combobox
        v-model="edited.tags"
        :items="allTags"
        :search-input.sync="tagInput"
        hide-selected
        label="Edit tags"
        multiple
        persistent-hint
        chips
        deletable-chips
      >
        <template v-slot:no-data>
          <v-list-item>
            <v-list-item-content>
              <v-list-item-title>
                No results matching "<strong>{{ tagInput }}</strong
                >". Press <kbd>enter</kbd> to create a new one
              </v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </template>
      </v-combobox>
      <!-- END: Editing -->
    </v-card-text>
    <v-card-actions>
      <v-btn text x-small v-on:click="$emit('complete-edit', edited)">
        <v-icon>mdi-check</v-icon>
        Finish
      </v-btn>
      <v-btn text x-small v-on:click="$emit('cancel-edit')">
        <v-icon>mdi-cancel</v-icon>
        Cancel
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
export default {
  props: ["bookmark", "allTags"],

  data() {
    return {
      edited: {
        id: this.bookmark.id,
        description: this.bookmark.description.slice(),
        tags: this.bookmark.tags.slice()
      },
      tagInput: null
    };
  }
};
</script>
