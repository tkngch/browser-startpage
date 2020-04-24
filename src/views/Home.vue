<template>
  <v-container fluid fill-height>
    <v-row align="center" class="mx-auto" justify="center">
      <v-col align="center" class="text-center" cols="12">
        <span class="font-weight-light display-4">
          {{ timeString }}
        </span>
        <br />
        <span class="font-weight-light display-1">
          {{ dateString }}
        </span>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
function padZero(num) {
  return (parseInt(num, 10) >= 10 ? "" : "0") + num;
}

export default {
  name: "Home",

  data() {
    return { dateString: "", timeString: "" };
  },

  created() {
    this.updateDatetime();
    this.datetimeUpdater = setInterval(this.updateDatetime, 1000);
  },

  beforeDestroy() {
    clearInterval(this.datetimeUpdater);
  },

  methods: {
    updateDatetime() {
      let now = new Date();

      let monthFormatter = new Intl.DateTimeFormat("gb", { month: "long" });
      let month = monthFormatter.format(now);
      let dateNumber = padZero(now.getDate());
      let year = padZero(now.getFullYear());
      this.dateString = dateNumber + " " + month + " " + year;

      let hours = padZero(now.getHours());
      let minutes = padZero(now.getMinutes());
      let seconds = padZero(now.getSeconds());

      this.timeString = hours + ":" + minutes + ":" + seconds;
    }
  }
};
</script>
