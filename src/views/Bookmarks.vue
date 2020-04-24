<template>
  <v-container fluid>
    <!-- Alert windows -->
    <v-alert dismissible type="success" v-if="messages.success">
      {{ messages.success }}
    </v-alert>
    <v-alert dismissible type="info" v-if="messages.info">
      {{ messages.info }}
    </v-alert>
    <v-alert dismissible type="warning" v-if="messages.warning">
      {{ messages.warning }}
    </v-alert>
    <v-alert dismissible type="error" v-if="messages.error">
      {{ messages.error }}
    </v-alert>
    <!-- END: Alert windows -->

    <v-row align="start" justify="start">
      <v-col cols="3">
        <BookmarkMenu
          v-bind:allTags="allTags"
          v-bind:allStatusCodes="allStatusCodes"
          v-bind:sortOptions="sortOptions"
          v-on:create-bookmark="createBookmark($event)"
          v-on:filter-bookmarks="filterBy = $event"
          v-on:sort-bookmarks="sortBy = $event"
        />
      </v-col>

      <v-col>
        <v-row align="start" justify="start">
          <v-col
            cols="4"
            v-for="bookmark in bookmarksToShow"
            :key="bookmark.id"
          >
            <BookmarkItem
              v-if="!isEditActive[bookmark.id]"
              v-bind:bookmark="bookmark"
              v-on:edit-bookmark="isEditActive[bookmark.id] = true"
              v-on:sync-bookmark="syncBookmark(bookmark)"
              v-on:delete-bookmark="deleteBookmark(bookmark)"
              v-on:visit-bookmark="visitBookmark(bookmark)"
            />
            <BookmarkEdit
              v-else
              v-bind:bookmark="bookmark"
              v-bind:allTags="allTags"
              v-on:cancel-edit="isEditActive[bookmark.id] = false"
              v-on:complete-edit="completeEdit(bookmark, $event)"
            />
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import BookmarkMenu from "@/components/BookmarkMenu.vue";
import BookmarkItem from "@/components/BookmarkItem.vue";
import BookmarkEdit from "@/components/BookmarkEdit.vue";
import BookmarkService from "@/services/BookmarkService.js";

function filterBookmarks(bookmarks, filterBy) {
  console.log("Filtering by", filterBy);
  let filtered = bookmarks.filter(
    bookmark =>
      (filterBy.tags
        ? filterBy.tags.every(tag => bookmark.tags.includes(tag))
        : true) &&
      (filterBy.statusCode ? filterBy.statusCode == bookmark.statusCode : true)
  );
  return filtered;
}

function sortBookmarks(bookmarks, sortBy) {
  let desc = null;
  let key = null;
  switch (sortBy) {
    case "New":
      desc = true;
      key = "checkedDatetime";
      break;
    case "Old":
      desc = false;
      key = "checkedDatetime";
      break;
    case "Most Visits":
      desc = true;
      key = "visitCount";
      break;
    case "Least Visits":
      desc = false;
      key = "visitCount";
      break;
  }

  let sorted = bookmarks.slice();
  console.log("Sorting by", sortBy);

  if (desc !== null) {
    sorted.sort((bookmark0, bookmark1) => {
      if (
        !Object.prototype.hasOwnProperty.call(bookmark0, key) ||
        !Object.prototype.hasOwnProperty.call(bookmark1, key)
      ) {
        return 0;
      }
      let comparison = 0;
      if (bookmark0[key] > bookmark1[key]) {
        comparison = 1;
      } else if (bookmark0[key] < bookmark1[key]) {
        comparison = -1;
      }
      return desc ? comparison * -1 : comparison;
    });
  }

  return sorted;
}

export default {
  name: "bookmarks",

  components: {
    BookmarkMenu,
    BookmarkItem,
    BookmarkEdit
  },

  data() {
    return {
      messages: { success: "", info: "", warning: "", error: "" },
      bookmarks: [],
      isEditActive: {},
      filterBy: { tags: [], statusCode: null },
      sortBy: null,
      sortOptions: ["New", "Old", "Most Visits", "Least Visits"]
    };
  },

  mounted() {
    BookmarkService.getBookmarks()
      .then(response => {
        this.bookmarks = response.data;
        this.bookmarks.forEach(bookmark => {
          this.$set(this.isEditActive, bookmark.id, false);
        });
      })
      .catch(error => (this.messages.error = error));
  },

  computed: {
    filteredBookmarks: function() {
      return filterBookmarks(this.bookmarks, this.filterBy);
    },

    bookmarksToShow: function() {
      return sortBookmarks(this.filteredBookmarks, this.sortBy);
    },

    allTags: function() {
      let tags = this.bookmarks.map(bookmark => bookmark.tags).flat(1);
      return Array.from(new Set(tags)).sort();
    },

    allStatusCodes: function() {
      let codes = this.bookmarks.map(bookmark => bookmark.statusCode).flat(1);
      return Array.from(new Set(codes)).sort();
    }
  },

  methods: {
    createBookmark(newBookmarkURL) {
      console.log("Creating", newBookmarkURL);
      BookmarkService.postBookmarks([newBookmarkURL])
        .then(response => {
          this.bookmarks = response.data.concat(this.bookmarks);
          response.data.forEach(entry =>
            this.$set(this.isEditActive, entry.id, false)
          );
        })
        .catch(
          error =>
            (this.messages.error =
              "Failed to create a bookmark '" + newBookmarkURL + "'. " + error)
        );
    },

    syncBookmark(bookmark) {
      console.log("Syncing", bookmark.title);
      BookmarkService.putBookmarks([bookmark])
        .then(response => {
          let filtered = this.bookmarks.filter(bm => bm.id !== bookmark.id);
          this.bookmarks = response.data.concat(filtered);
        })
        .catch(error => (this.messages.error = error));
    },

    deleteBookmark(bookmark) {
      console.log("Deleting", bookmark.title);
      this.bookmarks = this.bookmarks.filter(bm => bm.id !== bookmark.id);
      BookmarkService.deleteBookmarks([bookmark])
        .then(() => {
          this.messages.success = "Bookmark deleted.";
          setTimeout(() => (this.messages.success = ""), 3000);
        })
        .catch(error => (this.messages.error = error));
    },

    completeEdit(bookmark, edited) {
      this.isEditActive[bookmark.id] = false;

      console.log("Updating", bookmark.title);
      BookmarkService.patchBookmarks([edited])
        .then(response => {
          let index = this.bookmarks.findIndex(bm => bm.id === bookmark.id);
          this.bookmarks.splice(index, 1, response.data[0]);

          this.messages.success = "Bookmark edited.";
          setTimeout(() => (this.messages.success = ""), 3000);
        })
        .catch(error => (this.messages.error = error));
    },

    visitBookmark(bookmark) {
      console.log("Visiting", bookmark.title);
      BookmarkService.visitBookmark(bookmark)
        .then(response => {
          let index = this.bookmarks.findIndex(bm => bm.id === bookmark.id);
          this.bookmarks.splice(index, 1, response.data);
        })
        .catch(error => (this.messages.error = error));
    }
  }
};
</script>
