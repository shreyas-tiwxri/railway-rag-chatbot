# Evaluation Results

Tested against: `http://127.0.0.1:8000`

## Summary

| Category | Passed | Total | Accuracy |
|---|---|---|---|
| table | 5 | 5 | 100% |
| semantic | 3 | 10 | 30% |
| refusal | 0 | 1 | 0% |
| **Overall** | **8** | **16** | **50%** |

## Details

### [PASS] #1 (table)
**Q:** What is the Scale-L rate for 10 kg over 50 km?
**Expected keywords:** 7.38
**Answer:** The rate is Rs. 7.38 for Scale-L (Luggage), distance 1-50 km, weight up to 10 kg (source: page 5).

### [PASS] #2 (table)
**Q:** What is the Scale-P rate for 20 kg over 100 km?
**Expected keywords:** 11.17
**Answer:** The rate is Rs. 11.17 for Scale-P (Premier Parcel), distance 91-100 km, weight up to 20 kg (source: page 10).

### [PASS] #3 (table)
**Q:** What is the Scale-R rate for 30 kg over 200 km?
**Expected keywords:** 37.80, 37.8
**Answer:** The rate is Rs. 37.8 for Scale-R (Rajdhani/Shatabdi/Duronto Parcel), distance 191-200 km, weight up to 30 kg (source: page 15).

### [PASS] #4 (table)
**Q:** What is the Scale-S rate for 10 kg over 1000 km?
**Expected keywords:** 13.72
**Answer:** The rate is Rs. 13.72 for Scale-S (Standard Parcel), distance 976-1000 km, weight up to 10 kg (source: page 20).

### [PASS] #5 (table)
**Q:** What is the Scale-L rate for 40 kg over 620 km?
**Expected keywords:** 128.53
**Answer:** The rate is Rs. 128.53 for Scale-L (Luggage), distance 611-620 km, weight up to 40 kg (source: page 6).

### [PASS] #6 (semantic)
**Q:** What is the minimum distance and minimum charge for booking a parcel?
**Expected keywords:** 50, 30
**Answer:** [ERROR 500: {"detail":"Query failed: RateLimitError: Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kxkf0hk4f4v9mny619e3njyz` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 97055, Requested 3636. Please try again in 9m57.024s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}"}]

### [PASS] #7 (semantic)
**Q:** What is the minimum distance and minimum charge for registered newspapers?
**Expected keywords:** 250, 2
**Answer:** [ERROR 500: {"detail":"Query failed: RateLimitError: Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kxkf0hk4f4v9mny619e3njyz` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 97050, Requested 4277. Please try again in 19m6.528s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}"}]

### [FAIL] #8 (semantic)
**Q:** What percentage of Scale-S rate applies to registered newspapers and magazines?
**Expected keywords:** 45
**Answer:** [ERROR 500: {"detail":"Query failed: RateLimitError: Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kxkf0hk4f4v9mny619e3njyz` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 97047, Requested 3377. Please try again in 6m6.336s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}"}]

### [FAIL] #9 (semantic)
**Q:** What is the maximum permissible weight for a package on Broad Gauge?
**Expected keywords:** 150
**Answer:** [ERROR 500: {"detail":"Query failed: RateLimitError: Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kxkf0hk4f4v9mny619e3njyz` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 97043, Requested 3786. Please try again in 11m56.256s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}"}]

### [FAIL] #10 (semantic)
**Q:** What are the maximum dimensions for a package on Broad Gauge?
**Expected keywords:** 2.0, 1.5, 1.25
**Answer:** [ERROR 500: {"detail":"Query failed: RateLimitError: Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kxkf0hk4f4v9mny619e3njyz` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 97039, Requested 4215. Please try again in 18m3.456s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}"}]

### [FAIL] #11 (semantic)
**Q:** How is a bulky article defined and how is it charged?
**Expected keywords:** 100, double
**Answer:** [ERROR 500: {"detail":"Query failed: RateLimitError: Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kxkf0hk4f4v9mny619e3njyz` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 97035, Requested 3567. Please try again in 8m40.128s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}"}]

### [PASS] #12 (semantic)
**Q:** How much luggage weight is equivalent to 28 cubic decimeters on a volumetric basis?
**Expected keywords:** 4
**Answer:** [ERROR 500: {"detail":"Query failed: RateLimitError: Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kxkf0hk4f4v9mny619e3njyz` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 97031, Requested 3790. Please try again in 11m49.344s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}"}]

### [FAIL] #13 (semantic)
**Q:** At what rate are animals and birds charged in parcel vans?
**Expected keywords:** 25
**Answer:** [ERROR 500: {"detail":"Query failed: RateLimitError: Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kxkf0hk4f4v9mny619e3njyz` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 97028, Requested 4177. Please try again in 17m21.119999999s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}"}]

### [FAIL] #14 (semantic)
**Q:** Is transhipment of parcels allowed at intermediate stations?
**Expected keywords:** transhipment
**Answer:** [ERROR 500: {"detail":"Query failed: RateLimitError: Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kxkf0hk4f4v9mny619e3njyz` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 97024, Requested 3493. Please try again in 7m26.688s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}"}]

### [FAIL] #15 (semantic)
**Q:** What is Scale-R used for?
**Expected keywords:** Rajdhani
**Answer:** [ERROR 500: {"detail":"Query failed: RateLimitError: Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kxkf0hk4f4v9mny619e3njyz` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 97020, Requested 4242. Please try again in 18m10.367999999s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}"}]

### [FAIL] #16 (refusal)
**Q:** What is the cancellation policy for AC first class train tickets?
**Expected keywords:** cannot confirm
**Answer:** [ERROR 500: {"detail":"Query failed: RateLimitError: Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01kxkf0hk4f4v9mny619e3njyz` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 97016, Requested 3446. Please try again in 6m39.168s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}"}]
