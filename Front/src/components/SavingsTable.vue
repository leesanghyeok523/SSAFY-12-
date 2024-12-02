
<template>
  <div class="savings-table-container">
    <h2>저축 상품 목록</h2>
    <table class="savings-table">
      <thead>
        <tr>
          <th>상품명</th>
          <th>기본 이율 (%)</th>
          <th>최대 이율 (%)</th>
          <th>가입 방법</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="saving in savings" :key="saving.id">
          <td class="product-name">{{ saving.financial_product_name || "상품명 없음" }}</td>
          <td class="interest-rate">
            {{ saving.basic_interest_rate ? parseFloat(saving.basic_interest_rate).toFixed(2) : "정보 없음" }}
          </td>
          <td class="interest-rate">
            {{ saving.max_interest_rate ? parseFloat(saving.max_interest_rate).toFixed(2) : "정보 없음" }}
          </td>
          <td class="join-way">{{ saving.join_way || "정보 없음" }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  props: {
    savings: {
      type: Array,
      required: true,
    },
  },
};
</script>


<style scoped>
.savings-table-container {
  margin: 20px auto;
  padding: 20px;
  width: 90%;
  max-width: 1200px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  background: #ffffff;
  font-family: 'Roboto', sans-serif;
  text-align: center;
}

h2 {
  margin-bottom: 20px;
  font-size: 1.8rem;
  color: #333;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.savings-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.savings-table thead {
  background: linear-gradient(to right, #6a11cb, #2575fc);
  color: white;
}

.savings-table thead th {
  padding: 15px;
  font-size: 1rem;
  text-align: left;
}

.savings-table tbody tr {
  transition: background-color 0.3s ease;
}

.savings-table tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}

.savings-table tbody tr:hover {
  background-color: #f1f1f1;
}

.savings-table tbody td {
  padding: 15px;
  font-size: 0.9rem;
  color: #555;
  vertical-align: middle;
}

.product-name {
  font-weight: 600;
  color: #333;
}

.interest-rate {
  font-weight: 500;
  color: #007bff;
}

.join-way {
  color: #666;
  font-size: 0.85rem;
}

@media (max-width: 768px) {
  .savings-table-container {
    padding: 10px;
  }

  .savings-table thead th {
    font-size: 0.85rem;
  }

  .savings-table tbody td {
    font-size: 0.8rem;
    padding: 10px;
  }
}
</style>

