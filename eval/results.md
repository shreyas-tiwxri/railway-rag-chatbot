# Evaluation Results

Tested against: `http://127.0.0.1:8000`

## Summary

| Category | Passed | Total | Accuracy |
|---|---|---|---|
| table | 5 | 5 | 100% |
| semantic | 10 | 10 | 100% |
| refusal | 1 | 1 | 100% |
| **Overall** | **16** | **16** | **100%** |

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
**Answer:** According to [MX-M464N_20250116_182617.pdf, page 1] and [MX-M464N_20250116_182617.pdf, page 1], the minimum distance for charge is 100 km. 

Regarding the minimum charge, [Red Tariff.pdf, page 31] states that the minimum weight for charge per consignment when booked to be carried by goods train shall be 100 kgs. and by passenger, parcel or mixed train shall be 10 kgs. However, it does not explicitly mention the minimum charge. 

Therefore, based on the available information, the minimum distance for charge is 100 km, but the minimum charge is not explicitly stated in the provided context.

### [PASS] #7 (semantic)
**Q:** What is the minimum distance and minimum charge for registered newspapers?
**Expected keywords:** 250, 2
**Answer:** The minimum distance for charge for registered Newspapers and Magazines is 250 kilometers and the minimum charge is Rs. 2.00. (Source: [FM_21_Annexure_parcel_rate_table.pdf, page 3])

### [PASS] #8 (semantic)
**Q:** What percentage of Scale-S rate applies to registered newspapers and magazines?
**Expected keywords:** 45
**Answer:** According to [FM_21_Annexure_parcel_rate_table.pdf, page 3], Registered Newspapers & Magazines will continue to be booked at concessional rates uniformly at 45 percent of Scale-S by all trains including Rajdhani trains.

### [PASS] #9 (semantic)
**Q:** What is the maximum permissible weight for a package on Broad Gauge?
**Expected keywords:** 150
**Answer:** The maximum permissible weight for a package on Broad Gauge is 150 Kgs, as stated in [FM_21_Annexure_parcel_rate_table.pdf, page 3].

### [PASS] #10 (semantic)
**Q:** What are the maximum dimensions for a package on Broad Gauge?
**Expected keywords:** 2.0, 1.5, 1.25
**Answer:** The maximum dimensions for a package on Broad Gauge are 2.0 meters X 1.5 meters X 1.25 meters. (Source: [FM_21_Annexure_parcel_rate_table.pdf, page 3])

### [PASS] #11 (semantic)
**Q:** How is a bulky article defined and how is it charged?
**Expected keywords:** 100, double
**Answer:** According to [FM_21_Annexure_parcel_rate_table.pdf, page 3], a bulky article is defined as any package whose weight exceeds 100 kilograms or whose outside measurements exceed 1.0 meter X 1.0 meter X 0.7 meter. A tolerance of 10% in any one outside dimension is allowed. Such articles are charged at double the normal rates.

### [PASS] #12 (semantic)
**Q:** How much luggage weight is equivalent to 28 cubic decimeters on a volumetric basis?
**Expected keywords:** 4
**Answer:** According to [FM_21_Annexure_parcel_rate_table.pdf, page 3], 28 cubic decimeters of volume is equivalent to 4 kilograms on a volumetric basis.

### [PASS] #13 (semantic)
**Q:** At what rate are animals and birds charged in parcel vans?
**Expected keywords:** 25
**Answer:** According to [FM_21_Annexure_parcel_rate_table.pdf, page 2], animals and birds in Parcel Vans and Brake Vans are charged uniformly at Scale-L + 25%, irrespective of the category of the train.

### [PASS] #14 (semantic)
**Q:** Is transhipment of parcels allowed at intermediate stations?
**Expected keywords:** transhipment
**Answer:** According to [SN-18.pdf, page 1], transhipment of parcels from a train and reloading the same into another train at any intermediate station is not permitted except for booking via break-of-gauge station. However, [SN-18.pdf, page 2] mentions that transhipment of parcels at intermediate stations was permitted for parcels loaded in COVID-19 Parcel Special trains, but this relaxation was only till the restoration of normal passenger-carrying trains. 

It is further clarified in [SN-18.pdf, page 1] that the relaxations regarding transhipment of parcels were permitted only in COVID-19 Parcel Special trains, and not in passenger-carrying trains. 

Therefore, as per the available documents, transhipment of parcels at intermediate stations is generally not allowed, except in specific cases like booking via break-of-gauge station, or as per specific relaxations that may be in place during exceptional circumstances.

### [PASS] #15 (semantic)
**Q:** What is Scale-R used for?
**Expected keywords:** Rajdhani
**Answer:** Scale-R is used for charging of freight for booking of parcel traffic under Rajdhani/Shatabdi/Duronto trains, as stated in [FM_21_Annexure_parcel_rate_table.pdf, page 1] and [FM_21_Annexure_parcel_rate_table.pdf, page 2]. It is one of the three scales, along with Scale-P and Scale-S, used for different types of parcel services.

### [PASS] #16 (refusal)
**Q:** What is the cancellation policy for AC first class train tickets?
**Expected keywords:** cannot confirm
**Answer:** I cannot confirm this from the available documents.
