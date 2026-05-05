import streamlit as st
import matplotlib.pyplot as plt

# --- TITLE ---
st.title("CGT Policy Simulator: Growth vs Inflation")

# --- USER INPUTS ---
purchase_price = st.slider("Purchase price ($)", 100000, 2000000, 800000)
tax_rate = st.slider("Tax rate", 0.0, 0.5, 0.45)

growth_rate = st.slider("Price growth rate", 0.0, 0.1, 0.05)
inflation_rate = st.slider("Inflation rate", 0.0, 0.1, 0.03)

years_held = st.slider("Holding period (years)", 1, 40, 10)

# --- NEW: policy timing ---
policy_change_year = st.slider("Policy change occurs in (years)", 1, 20, 5)

# --- FUNCTIONS ---

def cgt_current_growth(purchase_price, tax_rate, growth_rate, years):
    sale_price = purchase_price * (1 + growth_rate) ** years
    gain = sale_price - purchase_price
    taxable_gain = 0.5 * gain
    tax = taxable_gain * tax_rate
    return tax, sale_price


def cgt_indexation_growth(purchase_price, tax_rate, inflation_rate, growth_rate, years):
    sale_price = purchase_price * (1 + growth_rate) ** years
    indexed_cost = purchase_price * (1 + inflation_rate) ** years
    gain = sale_price - indexed_cost
    taxable_gain = max(gain, 0)
    tax = taxable_gain * tax_rate
    return tax, sale_price

# --- CURRENT CALCULATIONS ---
tax_current, sale_price = cgt_current_growth(
    purchase_price,
    tax_rate,
    growth_rate,
    years_held
)

tax_index, _ = cgt_indexation_growth(
    purchase_price,
    tax_rate,
    inflation_rate,
    growth_rate,
    years_held
)

# --- DISPLAY RESULTS ---
st.subheader("Results")

st.write(f"Projected sale price: ${sale_price:,.0f}")
st.write(f"Current system tax: ${tax_current:,.0f}")
st.write(f"Indexation tax: ${tax_index:,.0f}")
st.write(f"Difference (Indexation - Current): ${tax_index - tax_current:,.0f}")

# --- CHART: TAX VS HOLDING PERIOD ---
years_range = list(range(1, 41))

tax_current_list = []
tax_index_list = []

for y in years_range:
    
    t_current, _ = cgt_current_growth(
        purchase_price,
        tax_rate,
        growth_rate,
        y
    )
    
    t_index, _ = cgt_indexation_growth(
        purchase_price,
        tax_rate,
        inflation_rate,
        growth_rate,
        y
    )
    
    tax_current_list.append(t_current)
    tax_index_list.append(t_index)

fig, ax = plt.subplots()

ax.plot(years_range, tax_index_list, label="Indexation")
ax.plot(years_range, tax_current_list, linestyle="--", label="Current system")

ax.set_xlabel("Holding Period (years)")
ax.set_ylabel("Tax ($)")
ax.set_title("CGT: Growth vs Inflation Interaction")
ax.legend()

st.pyplot(fig)

# =====================================================
# 🧠 NEW FEATURE: SELL NOW VS LATER
# =====================================================

st.subheader("Sell Now vs After Policy Change")

# Sell BEFORE policy change
tax_now, sale_now = cgt_current_growth(
    purchase_price,
    tax_rate,
    growth_rate,
    policy_change_year
)

# Sell AFTER policy change (hold longer, new system applies)
years_after = years_held
tax_later, sale_later = cgt_indexation_growth(
    purchase_price,
    tax_rate,
    inflation_rate,
    growth_rate,
    years_after
)

st.write(f"Sell before reform (year {policy_change_year}): ${tax_now:,.0f}")
st.write(f"Sell after reform (year {years_after}): ${tax_later:,.0f}")
st.write(f"Tax difference (later - now): ${tax_later - tax_now:,.0f}")

# --- VISUAL COMPARISON ---
fig2, ax2 = plt.subplots()

ax2.bar(["Sell Before Reform", "Sell After Reform"], [tax_now, tax_later])

ax2.set_ylabel("Tax ($)")
ax2.set_title("Sell Now vs Later")

st.pyplot(fig2)