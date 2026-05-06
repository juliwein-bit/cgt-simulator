import streamlit as st
import matplotlib.pyplot as plt

# --- PAGE CONFIG ---
st.set_page_config(page_title="Asset Sale Timing under CGT Reform", layout="wide")

# --- TITLE ---
st.title("Asset Sale Timing under CGT Reform")


# =====================================================
# INTRODUCTION (PURPOSE + MODEL OVERVIEW)
# =====================================================

st.markdown("""
### About this tool

Australia is considering changes to its Capital Gains Tax (CGT) regime, including the introduction of indexation.  
The timing and final design of these changes remain uncertain. This tool helps users explore how policy timing, growth, inflation, and discounting interact when evaluating asset sale timing decisions. 
### What the model does 

The model compares after-tax outcomes across different selling times under a range of economic and policy assumptions.

For each possible selling year, it:

- Projects the future value of the asset from its current estimated market value using the assumed growth rate  
- Applies the relevant tax treatment depending on whether the policy has started  
- Calculates after-tax proceeds  
- Converts those proceeds into present value terms using a discount rate  

It then compares outcomes across selling times to show how timing affects estimated after-tax value under the assumptions provided. Right now, your model implicitly applies indexation retrospectively to the entire holding period.


""")



# =====================================================
# INPUTS
# =====================================================

st.sidebar.header("Inputs")

purchase_price = st.sidebar.slider("Original Purchase Price ($)", 100000, 2000000, 800000)

current_market_value = st.sidebar.slider("Current Estimated Market Value ($)", 100000, 5000000, 1200000)

tax_rate = st.sidebar.slider("Marginal Tax Rate (%)", 0, 50, 45) / 100
growth_rate = st.sidebar.slider("Price Growth Rate (yearly average) (%)", 0, 10, 5) / 100
inflation_rate = st.sidebar.slider("Inflation Rate (yearly average) (%)", 0, 10, 3) / 100
discount_rate = st.sidebar.slider("Discount Rate (yearly average) (%)", 0, 10, 5) / 100

sell_year = st.sidebar.slider("Planned Selling Year", 1, 40, 10)
policy_start = st.sidebar.slider("Time Until Indexation Starts (years)", 0.1, 5.0, 0.3)

# =====================================================
# FUNCTIONS
# =====================================================

def cgt_current_growth(purchase_price, tax_rate, growth_rate, years):
    sale_price = current_market_value * (1 + growth_rate) ** years
    gain = sale_price - purchase_price
    taxable_gain = 0.5 * gain
    tax = taxable_gain * tax_rate
    return tax, sale_price


def cgt_indexation_growth(purchase_price, tax_rate, inflation_rate, growth_rate, years):
    sale_price = current_market_value * (1 + growth_rate) ** years
    indexed_cost = purchase_price * (1 + inflation_rate) ** years
    gain = sale_price - indexed_cost
    taxable_gain = max(gain, 0)
    tax = taxable_gain * tax_rate
    return tax, sale_price


def calculate_after_tax_npv(year):
    if year <= policy_start:
        tax, sale_price = cgt_current_growth(purchase_price, tax_rate, growth_rate, year)
    else:
        tax, sale_price = cgt_indexation_growth(purchase_price, tax_rate, inflation_rate, growth_rate, year)
    
    after_tax = sale_price - tax
    npv = after_tax / ((1 + discount_rate) ** year)
    
    return npv, tax, sale_price

# =====================================================
# CURRENT SELECTION
# =====================================================

npv, tax, sale_price = calculate_after_tax_npv(sell_year)

# =====================================================
# SCENARIO ANALYSIS (OPTIMISATION)
# =====================================================

years_range = list(range(1, 41))

npv_values = []
tax_values = []

for y in years_range:
    n, t, _ = calculate_after_tax_npv(y)
    npv_values.append(n)
    tax_values.append(t)

best_year = years_range[npv_values.index(max(npv_values))]
best_npv = max(npv_values)

# =====================================================
# RESULTS
# =====================================================

st.subheader("Comparison of Selling Timings")

col1, col2 = st.columns(2)

# --- Selected scenario ---
col1.markdown("**Selected Scenario**")
col1.metric("Selling Year", f"{sell_year}")
col1.metric("Tax", f"${tax:,.0f}")
col1.metric("NPV", f"${npv:,.0f}")

# --- Best scenario ---
col2.markdown("**Highest Value Scenario (Model Output)**")
col2.metric("Selling Year", f"{best_year}")
col2.metric("Tax", f"${tax_values[years_range.index(best_year)]:,.0f}")
col2.metric("NPV", f"${best_npv:,.0f}")

# Difference explanation
difference = best_npv - npv

st.markdown("### Interpretation")

if difference > 0:
    st.write(
        f"Under the current assumptions, the highest-value scenario results in an estimated increase of approximately ${difference:,.0f} in present value terms relative to the selected timing."
    )
else:
    st.write(
        "Under the current assumptions, the selected timing produces an outcome consistent with the highest estimated value."
    )

# =====================================================
# 🧠 DYNAMIC EXPLANATION (SMART BUT SAFE)
# =====================================================

st.markdown("### Interpretation")

if discount_rate > growth_rate:
    st.write(
        "This outcome is primarily driven by the discount rate exceeding the expected growth rate, which reduces the present value of waiting."
    )
elif growth_rate > discount_rate:
    st.write(
        "This outcome is influenced by expected growth exceeding the discount rate, increasing the value of holding the asset for longer."
    )
else:
    st.write(
        "This outcome reflects a balance between growth and discounting, where timing effects become more sensitive to tax treatment."
    )

if inflation_rate > growth_rate:
    st.write(
        "Higher inflation relative to growth reduces real gains, which limits taxable gains under indexation."
    )
elif growth_rate > inflation_rate:
    st.write(
        "Positive real growth results in taxable gains even under indexation, affecting the relative tax outcomes."
    )

# =====================================================
# NPV CHART
# =====================================================

st.markdown("---")
st.subheader("Present Value of After-Tax Outcomes Across Selling Scenarios")

fig, ax = plt.subplots()

# Main line
ax.plot(years_range, npv_values, label="NPV (after-tax, present value)")

# Policy change marker
ax.axvline(policy_start, linestyle=":", label="Policy change timing")

# Optimal point
ax.scatter(best_year, best_npv, label="Highest value scenario")

ax.set_xlabel("Years")
ax.set_ylabel("NPV ($)")


ax.legend()  # 👈 this is key

st.pyplot(fig)


# =====================================================
# GOVERNMENT REVENUE VIEW
# =====================================================

st.markdown("---")
st.subheader("Government Revenue Comparison")

st.markdown("""
This section illustrates how tax collected differs across systems.

It is provided for context and does not affect the scenario comparison above.
""")

tax_current_list = []
tax_index_list = []

for y in years_range:
    t_current, _ = cgt_current_growth(purchase_price, tax_rate, growth_rate, y)
    t_index, _ = cgt_indexation_growth(purchase_price, tax_rate, inflation_rate, growth_rate, y)
    
    tax_current_list.append(t_current)
    tax_index_list.append(t_index)

fig2, ax2 = plt.subplots()

ax2.plot(years_range, tax_current_list, linestyle="--", label="Current System")
ax2.plot(years_range, tax_index_list, label="Indexation")

ax2.set_xlabel("Years")
ax2.set_ylabel("Tax Collected ($)")
ax2.legend()

st.pyplot(fig2)

tax_current_selected, _ = cgt_current_growth(purchase_price, tax_rate, growth_rate, sell_year)
tax_index_selected, _ = cgt_indexation_growth(purchase_price, tax_rate, inflation_rate, growth_rate, sell_year)

tax_difference = tax_current_selected - tax_index_selected

st.metric("Difference in tax collected (selected year)", f"${tax_difference:,.0f}")

# =====================================================
# EXPLANATION SECTION (END)
# =====================================================

st.markdown("---")
st.subheader("Model Explanation")

st.markdown("""
### Why outcomes differ across scenarios

Different selling times produce different outcomes because:

- Asset values evolve over time  
- Tax treatment may change depending on policy timing  
- Future proceeds are discounted back to present value  

---

### What is the discount rate?

The discount rate reflects how much future money is valued relative to today.

- Higher discount rate → future proceeds are worth less  
- Lower discount rate → future proceeds retain more value  

It plays a central role in comparing earlier versus later outcomes.
""")

# =====================================================
# DISCLAIMER
# =====================================================

st.markdown("---")
st.caption("""
This tool is provided for illustrative purposes only and is based on simplified assumptions.  
It does not constitute financial, tax, or investment advice.  
Users should seek professional advice before making financial decisions.
""")