
simple strategy description in string, end user only need to provide it
----
(price[0] > sma5[0] + 0.5) & (price[0] < sma20[0])

price[0] > price[-1]
-----

empty line is for step doing nothing


-------------------------------------------
tk
gate, filter

sn, type, input_list, condition, output_list

0,  gate,   ,   (sma20[0] > price[0]),  list_0
1, filter, list_0, (sma5[0] > price[0] and slope[0] < 0.9),  list_1
2, filter, list_1, (sma5[0] > price[0] and slope[0] < 0.9),  list_2
