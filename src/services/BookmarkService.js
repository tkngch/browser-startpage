import axios from "axios";

const apiClient = axios.create({
  baseURL: `http://localhost:33875/api`,
  withCredentials: false, // This is the default
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json"
  },
  timeout: 10000
});

export default {
  getBookmarks() {
    return apiClient.get("/v1/bookmarks");
  },

  /**
   * @param { string[] } urls
   */
  postBookmarks(urls) {
    // Add bookmarks
    let parameters = urls.map(url => {
      return { url: url };
    });
    return apiClient.post("/v1/bookmarks", parameters);
  },

  putBookmarks(bookmarks) {
    // Sync bookmarks
    let parameters = bookmarks.map(bookmark => {
      return { id: bookmark.id, url: bookmark.url };
    });
    return apiClient.put("/v1/bookmarks", parameters);
  },

  /**
   * @param { Object[] } edited
   * @param { string } edited[].description
   * @param { string[] } edited[].tags
   */
  patchBookmarks(edited) {
    // Update bookmarks
    return apiClient.patch("/v1/bookmarks", edited);
  },

  deleteBookmarks(bookmarks) {
    let parameters = bookmarks.map(bookmark => {
      return { id: bookmark.id };
    });
    return apiClient.delete("/v1/bookmarks", { data: parameters });
  },

  visitBookmark(bookmark) {
    let parameter = { id: bookmark.id, visitCount: bookmark.visitCount };
    return apiClient.patch("/v1/visit/bookmark", parameter);
  }
};
