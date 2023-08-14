<template>
  <div class="container" id="gist">
    <h1 v-if="videoUrl" id="heading">Video Editor</h1>

    <!-- Video player -->
    <div v-if="videoUrl === 'null'"></div>
    <div class="vid" v-else-if="videoUrl">
      <video width="800" height="500" id="vid" ref="videoPlayer"
        :src="`http://localhost:5000/uploaded_videos/${videoUrl}`" @timeupdate="updateSubtitleDisplay" controls>
        Your browser does not support the video tag.
      </video>
    </div>
    <br />

    <!-- Video uploader -->
    <div v-if="!videoUrl" class="file">
      <label for="file">Click to Upload Video
        <ion-icon name="cloud-upload-outline"></ion-icon>
      </label>
      <input name="Select File" id="file" type="file" @change="uploadVideo" accept="video/*" />
      <br />
    </div>
    <!-- Custom subtitle input -->

    <div v-show="videoUrl" class="editblock container2">
      <p style="color: #1e9bff">Subtitle</p>
      <textarea id="textsarea" v-model="newSubtitle.text" placeholder="Enter your subtitle"
        class="txtarea from-text to-text" rows="1"></textarea>
      <br /><br />
      <p style="color: #1e9bff">TimeStamp</p>
      <br />
      <input id="timestmp" v-model="newSubtitle.timestamp" type="number" placeholder="Timestamp (seconds)" />
      <!-- Button to fetch and display subtitles -->
      <a class="btn3 button-70" @click="addSubtitle">Add</a><a class="button-70" @click="fetchAndDisplaySubtitles">Fetch
        Subtitles</a>
      <!-- Translator -->
      <div v-show="videoUrl">
        <h1 style="color: #1e9bff" id="subheading">Translator</h1>
        <div class="wrapper">
          <div class="text-input">
            <ul class="controls">
              <li class="row from">
                <div class="icons">
                  <ion-icon id="from" name="volume-medium-outline"></ion-icon>
                  <ion-icon id="from" name="copy-outline"></ion-icon>
                </div>
                <select></select>
              </li>
              <li class="exchange">
                <ion-icon name="swap-vertical"></ion-icon>
              </li>
              <li class="row to">
                <select></select>
                <div class="icons">
                  <ion-icon id="to" name="volume-medium-outline"></ion-icon>
                  <ion-icon id="to" name="copy-outline"></ion-icon>
                </div>
              </li>
            </ul>
          </div>
        </div>
        <button class="transbtn2">Translate</button>
      </div>
    </div>

    <!-- Subtitle display -->
    <div class="subtitle-overlay" v-if="activeSubtitle">
      {{ activeSubtitle.text }}
    </div>

    <!-- Existing subtitles -->
    <div v-if="videoUrl && subtitles.length > 0" id="sub_info">
      <h1 style="color: #1e9bff" id="subheading" v-if="videoUrl && subtitles.length > 0">
        Subtitles
      </h1>

      <div v-for="(subtitle, index) in subtitles" :key="index">
        <span id="sub_text">{{ subtitle.text }} ({{ subtitle.timestamp }} seconds)</span>
        <button class="fa fa-close" style="
             {
              color: #1e9bff;
            }
          " @click="removeSubtitle(index)"></button>
      </div>
      <div class="containerbtn" v-if="subtitles.length > 0" @click="uploadSubtitles">
        <div class="button">
          <div class="icon">
            <i class="fa fa-upload"></i>
          </div>
        </div>
        <p>Upload</p>

      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import axiosInstance from "./axiosinstance"; // Update the path based on your folder structure
import postscribe from "postscribe";

export default {
  /* eslint-disable no-useless-escape */
  // Importing script.js as external js
  mounted() {
    postscribe("#gist", `<script src="./script.js"><\/script>`);
  },
  data() {
    return {
      // Declaration of data vairables
      videoUrl: null,
      subtitles: [],
      newSubtitle: {
        text: "",
        timestamp: 0,
      },
      activeSubtitle: null,
    };
  },
  methods: {
    //Upload handle function
    uploadVideo(event) {
      const file = event.target.files[0];
      const formData = new FormData();
      formData.append("video", file);

      axiosInstance
        .post("/api/upload", formData)
        .then((response) => {
          this.videoUrl = response.data.video_url;
        })
        .catch((error) => {
          console.error("Video upload failed:", error);
        });
    },

    playVideoWithSubtitles() {
      // Generate a video with subtitles and play it
      axios
        .get(
          `http://localhost:5000/api/generate_video_with_subtitles/${this.videoUrl}`
        )
        .then((response) => {
          const videoUrlWithSubtitles = response.data.video_url;
          const videoPlayer = this.$refs.videoPlayer;
          videoPlayer.src = `http://localhost:5000/uploaded_videos/${videoUrlWithSubtitles}`;
          videoPlayer.load();
          videoPlayer.play();
        })
        .catch((error) => {
          console.error("Failed to generate video with subtitles:", error);
        });
    },
    fetchAndDisplaySubtitles() {
      // Fetch and display subtitles associated with the current video
      axios
        .get(`http://localhost:5000/api/subtitles/${this.videoUrl}`)
        .then((response) => {
          this.subtitles = response.data;
        })
        .catch((error) => {
          console.error("Failed to fetch subtitles:", error);
        });
    },
    addSubtitle() {
      let textval = document.getElementById("textsarea").value;
      if (this.newSubtitle.text && this.newSubtitle.timestamp >= 0) {
        this.subtitles.push({
          text: textval, // Use the translated text from newSubtitle
          timestamp: this.newSubtitle.timestamp,
          duration: 3, // You can set a default duration or calculate based on next subtitle timestamp
        });

        // Clear the input fields
        this.newSubtitle.text = ""; // Clear the translated text as well
        this.newSubtitle.timestamp = 0;
      }
    },
    updateSubtitleDisplay() {
      const currentTime = this.$refs.videoPlayer.currentTime;
      const activeSubtitle = this.subtitles.find((subtitle) => {
        return (
          currentTime >= subtitle.timestamp &&
          currentTime < subtitle.timestamp + subtitle.duration
        );
      });
      this.activeSubtitle = activeSubtitle;
    },
    uploadSubtitles() {
      this.count += 1;
      console.log(this.subtitles);
      // Send the subtitles array to the backend to create and store the subtitles file
      axios
        .post(
          `http://localhost:5000/api/create_subtitles/${this.videoUrl}`,
          this.subtitles
        )
        .then((response) => {
          console.log(response.data.message);
          this.fetchSubtitles(); // Refresh subtitles after successful upload
          this.subtitles = []; // Clear the local subtitles array
        })
        .catch((error) => {
          console.error("Failed to create subtitles:", error);
        });
    },

    removeSubtitle(index) {
      this.subtitles.splice(index, 1);
    },
    // Fetch existing subtitles from the backend and populate this.subtitles
    fetchSubtitles() {
      axios
        .get("http://localhost:5000/api/get_subtitles")
        .then((response) => {
          this.subtitles = response.data;
        })
        .catch((error) => {
          console.error("Failed to fetch subtitles:", error);
        });
    },
  },
  chooseFile() {
    document.getElementById("fileInput").click();
  },
};
</script>
<style>@import './assets/styles_custom.css';
@import './assets/style.css';</style>
