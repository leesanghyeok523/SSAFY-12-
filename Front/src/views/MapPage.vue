<template>
  <div class="map-page">
    <v-container fluid>
      <v-row justify="center" class="mb-4">
        <v-col cols="12" sm="10" md="8" lg="6">
          <v-row justify="space-between" class="mb-3">
            <v-col cols="4">
              <v-select
                v-model="selectedRegion"
                :items="regions"
                label="광역시/도"
                dense
              ></v-select>
            </v-col>
            <v-col cols="4">
              <v-select
                v-model="selectedDistrict"
                :items="districts"
                label="시/군/구"
                dense
                :disabled="!selectedRegion"
              ></v-select>
            </v-col>
            <v-col cols="4">
              <v-text-field
                v-model="bankName"
                label="은행명"
                placeholder="은행명을 입력하세요"
                dense
              ></v-text-field>
            </v-col>
          </v-row>
          <v-btn color="primary" block @click="searchBank">
            <v-icon left>mdi-magnify</v-icon>
            찾기
          </v-btn>
        </v-col>
      </v-row>
      <v-row justify="center">
        <v-col cols="12" sm="10" md="8" lg="6">
          <div id="map" class="map-container"></div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from "vue";
import { regionDistricts, regions } from "@/components/RegionDistricts.js";

const MAP_API_KEY = import.meta.env.VITE_MAP_API_KEY;

// 지도 관련 상태 변수
const center = ref([37.566826, 126.9786567]); // 서울시청 좌표
const level = ref(3);
const mapInstance = ref(null);

// 필터 관련 상태 변수
const selectedRegion = ref("");
const selectedDistrict = ref("");
const bankName = ref("");
const districts = ref([]);

// Watch로 selectedRegion 값 변경 시 districts 업데이트
watch(selectedRegion, (newValue) => {
  console.log("선택된 광역시/도:", newValue);
  if (regionDistricts[newValue]) {
    districts.value = regionDistricts[newValue];
    console.log("업데이트된 시/군/구 목록:", districts.value);
  } else {
    districts.value = [];
    console.warn("선택된 지역에 대한 시/군/구 데이터가 없습니다.");
  }
});

// 지도 초기화
const initMap = () => {
  const mapContainer = document.getElementById("map");
  const mapOption = {
    center: new kakao.maps.LatLng(center.value[0], center.value[1]),
    level: level.value,
  };

  mapInstance.value = new kakao.maps.Map(mapContainer, mapOption);

  kakao.maps.event.addListener(mapInstance.value, "center_changed", () => {
    const latlng = mapInstance.value.getCenter();
    center.value = [latlng.getLat(), latlng.getLng()];
  });
};

// 은행 검색
const searchBank = () => {
  if (!selectedRegion.value || !selectedDistrict.value || !bankName.value) {
    alert("모든 필터를 입력해주세요!");
    return;
  }

  const keyword = `${selectedRegion.value} ${selectedDistrict.value} ${bankName.value}`;

  const ps = new kakao.maps.services.Places();
  ps.keywordSearch(keyword, (data, status) => {
    if (status === kakao.maps.services.Status.OK) {
      if (mapInstance.value) {
        mapInstance.value.setCenter(
          new kakao.maps.LatLng(data[0].y, data[0].x)
        );
      }

      data.forEach(displayMarker);
    } else {
      alert("검색 결과가 없습니다.");
    }
  });

  function displayMarker(place) {
    const marker = new kakao.maps.Marker({
      map: mapInstance.value,
      position: new kakao.maps.LatLng(place.y, place.x),
    });

    const infowindow = new kakao.maps.InfoWindow({ zIndex: 1 });
    kakao.maps.event.addListener(marker, "click", () => {
      infowindow.setContent(
        `<div style="padding:5px;font-size:12px;">${place.place_name}</div>`
      );
      infowindow.open(mapInstance.value, marker);
    });
  }
};

// 페이지 로드 시 지도 초기화
onMounted(() => {
  if (window.kakao && window.kakao.maps) {
    initMap();
  } else {
    const script = document.createElement("script");
    script.onload = () => kakao.maps.load(initMap);
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?autoload=false&appkey=${MAP_API_KEY}&libraries=services`;
    document.head.appendChild(script);
  }
});
</script>

<style scoped>
.map-page {
  padding-top: 80px;
  background-image: url('@/assets/mapPage.jpg');
  background-size: 2150px 1100px;
  background-repeat: no-repeat;
  background-position: center;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.map-container {
  width: 100%;
  height: 500px;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
}

.v-btn {
  margin-bottom: 10px;
  background: linear-gradient(to right, #6a11cb, #2575fc);
}

.v-select,
.v-text-field {
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  color: #000;
}

.v-select label,
.v-text-field label {
  color: #555;
}

.v-row {
  margin-bottom: 20px;
}

.v-btn {
  font-weight: bold;
  font-size: 16px;
}

.map-page .v-btn {
  margin-top: 10px;
}
</style>
