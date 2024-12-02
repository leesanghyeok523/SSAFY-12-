import { defineStore } from "pinia";
import axios from "axios";

export const useSavingsStore = defineStore("savings", {
  state: () => ({
    deposits: [],
    savings: [],
    loading: false,
  }),
  actions: {
    async fetchSavingsData() {
      try {
        this.loading = true;
        const token = localStorage.getItem("accessToken");
        if (!token) {
          throw new Error("로그인이 필요합니다.");
        }

        const savingsResponse = await axios.get(
          "http://127.0.0.1:8000/api/core/actions/savings-products/",
          {
            headers: { Authorization: `Token ${token}` },
          }
        );
        this.savings = Array.isArray(savingsResponse.data)
          ? savingsResponse.data
          : [];
        console.log("적금 데이터 로드 성공:", this.savings);

        const depositsResponse = await axios.get(
          "http://127.0.0.1:8000/api/core/actions/deposit-products/",
          {
            headers: { Authorization: `Token ${token}` },
          }
        );
        this.deposits = Array.isArray(depositsResponse.data)
          ? depositsResponse.data
          : [];
        console.log("예금 데이터 로드 성공:", this.deposits);
      } catch (error) {
        console.error("데이터를 가져오는 데 실패했습니다:", error);
        throw new Error("데이터를 가져오는 데 실패했습니다.");
      } finally {
        this.loading = false;
        console.log("데이터 로드 작업이 완료되었습니다.");
      }
    },
  },
});
