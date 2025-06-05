Thanks for sharing the code! Based on your message that there was a **"pasting error in the next chat,"** I assume you might have encountered an error message or something didn't work after pasting this into Streamlit.

While the code looks mostly well-structured, here are a few **common issues and necessary fixes** to watch for and implement to ensure it runs smoothly:

---

### ✅ Fixes and Improvements

#### 1. **Streamlit Button Behavior in `col2`**

You're using:

```python
if st.button("🔄 Refresh Data", type="primary"):
```

The parameter `type="primary"` **is not valid** in recent Streamlit versions for `st.button`. Remove it to avoid an error:

```python
if st.button("🔄 Refresh Data"):
```

---

#### 2. **`st.cache_data.clear()`**

`st.cache_data.clear()` is **only available in newer versions** of Streamlit. If you see an error like:

> AttributeError: module 'streamlit' has no attribute 'cache\_data'

Replace all instances of:

```python
@st.cache_data(ttl=300)
```

With:

```python
@st.cache(ttl=300)
```

And change the clear call to:

```python
st.legacy_caching.clear_cache()
```

Or better: **Ensure you're using Streamlit ≥ 1.18**, where `st.cache_data` is introduced.

To check your version:

```bash
pip show streamlit
```

---

#### 3. **Handling Empty `data` from Yahoo Finance**

In `fetch_stock_data`, you return `None, None` if `data` is empty. That works, but then in:

```python
prev_close = data['Close'].iloc[-2] if len(data) > 1 else current_price
```

You should add a check to prevent accessing `.iloc[-2]` if there's only one row. Better:

```python
prev_close = data['Close'].iloc[-2] if len(data['Close']) > 1 else data['Close'].iloc[-1]
```

---

#### 4. **Avoid UI Freezes on Data Load**

The F\&O fetching loop is slow. Consider reducing the number of stocks temporarily while testing or use async fetching (with something like `asyncio` and `aiohttp`, though not directly supported by `yfinance`).

---

#### 5. **Use of `.NS` Extension**

You assume `.NS` works for all stocks. Make sure you’re in an environment where Yahoo Finance supports NSE tickers. You can test by running:

```python
yf.Ticker('RELIANCE.NS').history(period="1d")
```

If it fails, the environment may not support NSE tickers.

---

#### 6. **Potential Fix: Replacing `st.cache_data` with Working Version**

If your environment errors on this, here's how you can temporarily fix it:

```python
try:
    from streamlit.runtime.caching import cache_data as st_cache
except ImportError:
    from streamlit import cache as st_cache  # fallback

@st_cache(ttl=300)
def fetch_stock_data(...):
    ...
```

---

### ✅ Summary of Fixes

| Issue                      | Fix                                   |
| -------------------------- | ------------------------------------- |
| `type="primary"` not valid | Remove from `st.button()`             |
| `st.cache_data` errors     | Use `@st.cache` or update Streamlit   |
| `.iloc[-2]` may error      | Add check on `len(data)`              |
| Data fetching slow         | Limit or async fetch                  |
| NSE tickers not working    | Check with `.NS` manually             |
| Cache clearing not working | Use `st.legacy_caching.clear_cache()` |

---

If you have a **specific error message from your environment or traceback**, please paste it here and I’ll help debug that directly too.

Would you like me to give you a **fixed version of the full script** with the above corrections applied?
