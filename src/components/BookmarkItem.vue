<!-- Card to show single bookmark entry -->
<template>
  <v-card class="mx-auto" max-width="400">
    <v-card-title>
      <a
        class="blue-grey--text"
        target="_blank"
        :href="bookmark.url"
        v-on:click="$emit('visit-bookmark')"
      >
        {{ bookmark.title }}
      </a>
    </v-card-title>
    <v-card-subtitle>
      <a
        class="blue-grey--text"
        target="_blank"
        :href="bookmark.url"
        v-on:click="$emit('visit-bookmark')"
      >
        {{ bookmark.url }}
      </a>
    </v-card-subtitle>
    <!-- Card content -->
    <v-card-text>
      <!-- Description -->
      {{ bookmark.description }}
      <!-- END: Description -->
      <!-- Tags -->
      <v-chip-group column>
        <v-chip v-for="tag in bookmark.tags" :key="tag">
          {{ tag }}
        </v-chip>
      </v-chip-group>
      <!-- END: Tags -->
      <!-- Stats -->
      <v-chip-group column>
        <!-- Status code -->
        <v-chip
          label
          small
          :color="200 <= bookmark.statusCode < 300 ? 'success' : 'warning'"
        >
          <v-avatar
            left
            :class="
              200 <= bookmark.statusCode < 300
                ? 'success lighten-1'
                : 'warning lighten-1'
            "
          >
            <v-icon>mdi-pulse</v-icon>
          </v-avatar>
          {{ bookmark.statusCode }}
        </v-chip>
        <!-- END: Status code -->
        <!-- Visit count -->
        <v-chip label small :color="colourVisitCount">
          <v-avatar left class="amber lighten-5">
            <v-icon color="grey darken-1">mdi-mouse</v-icon>
          </v-avatar>
          {{ bookmark.visitCount }}
        </v-chip>
        <!-- END: Visit count -->
        <!-- Update time -->
        <v-chip label small>
          <v-avatar left>
            <v-icon>mdi-calendar-refresh</v-icon>
          </v-avatar>
          {{ timeSinceUpdate }}
        </v-chip>
        <!-- END: Update time -->
      </v-chip-group>
      <!-- END: Stats -->
    </v-card-text>
    <!-- END: Card content -->
    <v-card-actions>
      <v-btn text x-small v-on:click="$emit('sync-bookmark')">
        <v-icon>mdi-sync</v-icon>
        Sync
      </v-btn>
      <v-btn text x-small v-on:click="$emit('edit-bookmark')">
        <v-icon>mdi-pencil</v-icon>
        Edit
      </v-btn>
      <v-btn text x-small v-on:click="$emit('delete-bookmark')">
        <v-icon>mdi-delete</v-icon>
        Delete
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
function getRelativeTime(timeDiff) {
  const diffSeconds = Math.round(timeDiff / 1000);
  if (diffSeconds < 60) {
    return "Just now";
  }

  const diffMinutes = Math.round(diffSeconds / 60);
  if (diffMinutes === 1) {
    return `${diffMinutes} minute ago`;
  } else if (diffMinutes < 60) {
    return `${diffMinutes} minutes ago`;
  }

  const diffHours = Math.round(diffMinutes / 60);
  if (diffHours === 1) {
    return `${diffHours} hour ago`;
  } else if (diffHours < 24) {
    return `${diffHours} hours ago`;
  }

  const diffDays = Math.round(diffHours / 24);
  if (diffDays === 1) {
    return `${diffDays} day ago`;
  }
  return `${diffDays} days ago`;
}

export default {
  props: ["bookmark"],

  data() {
    return { timeNow: new Date() };
  },

  created() {
    this.dateUpdater = setInterval(() => {
      this.timeNow = new Date();
    }, 1000 * 60);
  },

  beforeDestroy() {
    clearInterval(this.dateUpdater);
  },

  computed: {
    colourVisitCount() {
      if (this.bookmark.visitCount < 10) {
        return "amber lighten-5";
      } else if (this.bookmark.visitCount < 20) {
        return "amber lighten-4";
      } else if (this.bookmark.visitCount < 30) {
        return "amber lighten-3";
      } else if (this.bookmark.visitCount < 40) {
        return "amber lighten-2";
      } else if (this.bookmark.visitCount < 50) {
        return "amber lighten-1";
      } else if (this.bookmark.visitCount < 60) {
        return "amber darken-1";
      } else if (this.bookmark.visitCount < 70) {
        return "amber darken-2";
      } else if (this.bookmark.visitCount < 80) {
        return "amber darken-3";
      } else if (this.bookmark.visitCount < 90) {
        return "amber darken-4";
      } else {
        return "amber";
      }
    },

    updateTime() {
      return Date.parse(this.bookmark.checkedDatetime);
    },

    timeSinceUpdate() {
      let diff = this.timeNow - this.updateTime;
      return getRelativeTime(diff);
    }
  }
};
</script>
