# RAG-Challenge Test Set Review

## fact_qa

### q001

- question: Which brand did Holley identify as its largest brand in 2022?
- answer: Holley EFI
- source_doc: 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf p.7 chunk `511a4a9c6a50d200b21c84f7d683ae7f91993183`: Brands We have a strong portfolio of brands covering various product categories. Our portfolio consists of over 70 brands spanning across 30 product categories. Our top seven brands generated 68% of our sales in 2022. Holley EFI : Currently our largest brand and represented 14% of our sales for 2022. Our Holley EFI brand focuses on electronic fuel injection technology and showcases our new product development engine.
- notes: Direct fact question; evidence states Holley EFI was the largest brand and represented 14% of 2022 sales.

### q002

- question: In which states are CrossFirst Bank's branches strategically located?
- answer: Kansas, Missouri, Oklahoma, Texas, Arizona, Colorado and New Mexico.
- source_doc: e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf p.12 chunk `c11866753bb3dbc2bf4ce346afc745d48c47a9f2`: The Bank operates as a regional bank providing a broad offering of deposit and lending products to commercial and consumer clients. The Bank's branches are strategically located in Kansas, Missouri, Oklahoma, Texas, Arizona, Colorado and New Mexico. Our approach to banking starts with our extraordinary service commitment. Our approach is highly tailored to our clients with the ability to customize products and services to meet our clients' individual needs. In addition to our branch locations, we also offer private banking solutions and commercial banking solutions. Private banking services
- notes: Direct fact question with an explicit state list in one chunk.

### q003

- question: Which three businesses did Holley say it acquired in 2022?
- answer: John's Ind., Inc. ('John's'), Southern Kentucky Classics ('SKC'), and Vesta Motorsports USA, Inc., d.b.a. RaceQuip ('RaceQuip').
- source_doc: 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf
- difficulty: medium
- requires_rewrite: True
- requires_multi_hop: False
- evidence excerpt:
  - 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf p.5 chunk `f0e0e2b2d073c0a6ee3a7b2b38b852c13178f23e`: our brand lineup through a series of strategic acquisitions, including our 2022 acquisitions of substantially all the assets of John's Ind., Inc. ('John's'), Southern Kentucky Classics ('SKC'), and Vesta Motorsports USA, Inc., d.b.a. RaceQuip ('RaceQuip'), our 2021 acquisitions of substantially all the assets of AEM Performance Electronics ('AEM'), Classic Instruments LLC ('Classic Instruments'), ADS Precision Machining, Inc., d.b.a. Arizona Desert Shocks ('ADS'), Baer, Inc, d.b.a. Baer Brakes ('Baer'), Brothers Mail Order Industries, Inc., d.b.a. Brothers Trucks
- notes: Question asks for businesses acquired; evidence uses formal acquisition wording and legal names.

### q004

- question: To whom was Mercia's Faradion investment sold in January 2022?
- answer: India's Reliance New Energy Solar Ltd, a wholly owned subsidiary of India-based Reliance Industries Ltd.
- source_doc: ac9aa244462c80705c3ff046542c02c459989742.pdf
- difficulty: medium
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - ac9aa244462c80705c3ff046542c02c459989742.pdf p.18 chunk `9eb8d2808502531479f262a468b101e6dcfc400f`: Faradion was sold in January 2022 to India's Reliance New Energy Solar Ltd, a wholly owned subsidiary of India-based Reliance Industries Ltd, for £100.0million. Total cash proceeds back to Mercia's balance sheet of £19.4million resulted in a realised gain of £9.9million, generating a 4.4x return on Mercia's direct investment cost of £4.4million and a c.72% internal rate of return ('IRR') since the first direct investment in 2017.
- notes: Adds Mercia coverage with a direct acquisition-exit fact.

### q005

- question: Which UK regional locations did Mercia list for its teams?
- answer: Bristol, Manchester, Preston, Leeds, Newcastle, Sheffield, London and Henley-in-Arden.
- source_doc: ac9aa244462c80705c3ff046542c02c459989742.pdf
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - ac9aa244462c80705c3ff046542c02c459989742.pdf p.14 chunk `4b0c168aab6493db6e430a3e4c4433356a76ef65`: £119.6m Value of direct investment portfolio See more on page 26. investees We invest exclusively in the UK Our teams are conveniently based in the following eight regional locations across the UK. Bristol Manchester Preston Leeds Newcastle Sheffield London Henley-in-Arden
- notes: Mercia location-list fact with all locations in one chunk.

### q006

- question: What operating model does Tradition say its brokers use for revenues?
- answer: A pure agency model in which revenues primarily consist of commissions earned by matching trades, and only if a trade is matched.
- source_doc: 2779336b845a41544348abb7b3e6e5bd2ff893a2.pdf
- difficulty: medium
- requires_rewrite: True
- requires_multi_hop: False
- evidence excerpt:
  - 2779336b845a41544348abb7b3e6e5bd2ff893a2.pdf p.14 chunk `30d03d92c6638ea587d61ec742aca3bc99866518`: Our clients have access to a global network, in-depth market intelligence, specialised knowledge of local markets and products, and large pools of liquidity. They benefit from the anonymity that reduces the market impact of placing orders. For this, brokers are organised in around 300 different desks, each representing a centre of expertise in a given market segment. Operating on the basis of a pure agency model with no conflict of interest and no position taking, our revenues primarily consist of commissions earned by matching trades, and only if a trade is matched.
- notes: Question uses business wording while evidence uses the formal phrase 'pure agency model'.

### q007

- question: What non-GAAP measure does Yellow Pages say its CEO uses to measure performance?
- answer: Adjusted EBITDA less CAPEX.
- source_doc: 9d7a72445aba6860402c3acce75af02dc045f74d.pdf
- difficulty: medium
- requires_rewrite: True
- requires_multi_hop: False
- evidence excerpt:
  - 9d7a72445aba6860402c3acce75af02dc045f74d.pdf p.10 chunk `a7b872c29505954ed3d18f1a7aa1f46416643926`: Management's Discussion and Analysis Analysis of Consolidated Operating and Financial Results The President and Chief Executive Officer ('CEO') is the Chief Operating Decision Maker and he uses Income from operations before depreciation and amortization and restructuring and other charges (Adjusted EBITDA) less CAPEX, to measure performance. Definitions of these non-GAAP financial measures are provided on page 4 of this MD&A. The CEO also reviews revenues by similar products and services, such as Print and Digital. Fiscal year 2022 versus 2021 Revenues
- notes: Question uses CEO/performance wording; evidence names the Chief Operating Decision Maker and metric.

### q008

- question: When did CrossFirst say it opened its first branch?
- answer: 2007.
- source_doc: e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf p.11 chunk `0ec28091604e2b17833ea578499e803675ffefc5`: Since opening our first branch in 2007, we have grown organically primarily by establishing new branches, attracting new clients and expanding our relationships with existing clients, as well as through three strategic acquisitions. Since inception, our strategy has been to be a trusted partner providing customized financial solutions for our clients, which we believe has driven value for our stockholders. We are committed to a culture of serving our clients and communities in extraordinary ways by providing personalized, relationship-based banking. We believe that success is achieved through
- notes: Direct CrossFirst chronology fact.

### q009

- question: What trading symbol is listed for Holley's common stock?
- answer: HLLY.
- source_doc: 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf p.1 chunk `7320bd02fa692b3aab366e4ea803023f186d4948`: 87-1727560 (I.R.S. Employer Identification No.) 1801 Russellville Road, Bowling Green, KY 42101 (Address of principal executive offices) (270) 782-2900 (Registrant ' s telephone number, including area code) (Former name, former address and former fiscal year, if changed since last report) N/A Securities registered pursuant to Section 12(b) of the Act: Trading symbol(s) Name of each exchange on which registered Title of each class Common Stock, par value $0.0001 Warrants to Purchase Common Stock HLLY New York Stock Exchange New York Stock Exchange HLLY WS
- notes: Direct securities-listing fact from Holley's cover page.

### q010

- question: What organization awarded £31.4 million to Mercia's equity and debt funds?
- answer: The British Business Bank ('BBB').
- source_doc: ac9aa244462c80705c3ff046542c02c459989742.pdf
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - ac9aa244462c80705c3ff046542c02c459989742.pdf p.3 chunk `3e89fac0fc26b0ddce369677c80a82b532310549`: Annual Report & Accounts 2022 Mercia Asset Management PLC 1 Strategic report 2022 highlights Sale of Faradion Ltd with total proceeds of £19.4million £11.4million fair value movements ('FvM') in the direct investment portfolio, following continued commercial progress, including significant third-party investment into nDreams Operational highlights £31.4million awarded by the British Business Bank ('BBB') to Mercia's equity and debt funds c.£87million of cash returned to fund investors from successful realisations (2021: c.£27million)
- notes: Mercia operational highlight with clear awarding organization.

### q051

- question: What year was Holley founded?
- answer: 1903.
- source_doc: 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf p.5 chunk `506c552e1d504118617d1722e8e47503db17fd21`: Founded in 1903, Holley, Inc. ('Holley' or the 'Company') has been a part of the automotive industry for well over a century. We are a leading designer, marketer, and manufacturer of high-performance automotive aftermarket products for car and truck enthusiasts. Our products span a number of automotive platforms and are sold across multiple channels. We attribute a major component of our success to our brands, including 'Holley', 'APR', 'MSD' and 'Flowmaster', among others. In addition, we have recently added to our brand lineup through a series of strategic acquisitions, including our 2022
- notes: Direct company-history fact from Holley's business overview.

### q052

- question: About how many specialist desks did Tradition say its brokers are organized into?
- answer: Around 300 different desks.
- source_doc: 2779336b845a41544348abb7b3e6e5bd2ff893a2.pdf
- difficulty: easy
- requires_rewrite: True
- requires_multi_hop: False
- evidence excerpt:
  - 2779336b845a41544348abb7b3e6e5bd2ff893a2.pdf p.14 chunk `30d03d92c6638ea587d61ec742aca3bc99866518`: Our clients have access to a global network, in-depth market intelligence, specialised knowledge of local markets and products, and large pools of liquidity. They benefit from the anonymity that reduces the market impact of placing orders. For this, brokers are organised in around 300 different desks, each representing a centre of expertise in a given market segment. Operating on the basis of a pure agency model with no conflict of interest and no position taking, our revenues primarily consist of commissions earned by matching trades, and only if a trade is matched.
- notes: Uses 'specialist desks' wording while evidence says each desk is a centre of expertise.

### q053

- question: Which product-service categories does Yellow Pages say the CEO reviews revenues by?
- answer: Print and Digital.
- source_doc: 9d7a72445aba6860402c3acce75af02dc045f74d.pdf
- difficulty: medium
- requires_rewrite: True
- requires_multi_hop: False
- evidence excerpt:
  - 9d7a72445aba6860402c3acce75af02dc045f74d.pdf p.10 chunk `a7b872c29505954ed3d18f1a7aa1f46416643926`: Management's Discussion and Analysis Analysis of Consolidated Operating and Financial Results The President and Chief Executive Officer ('CEO') is the Chief Operating Decision Maker and he uses Income from operations before depreciation and amortization and restructuring and other charges (Adjusted EBITDA) less CAPEX, to measure performance. Definitions of these non-GAAP financial measures are provided on page 4 of this MD&A. The CEO also reviews revenues by similar products and services, such as Print and Digital. Fiscal year 2022 versus 2021 Revenues
- notes: Question asks for revenue categories; evidence says the CEO reviews revenues by Print and Digital.

### q054

- question: What did Mercia say about the geographic scope of its investing?
- answer: Mercia said it invests exclusively in the UK.
- source_doc: ac9aa244462c80705c3ff046542c02c459989742.pdf
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - ac9aa244462c80705c3ff046542c02c459989742.pdf p.14 chunk `4b0c168aab6493db6e430a3e4c4433356a76ef65`: £119.6m Value of direct investment portfolio See more on page 26. investees We invest exclusively in the UK Our teams are conveniently based in the following eight regional locations across the UK. Bristol Manchester Preston Leeds Newcastle Sheffield London Henley-in-Arden
- notes: Direct Mercia fact about investment geography.

### q055

- question: What did CrossFirst say its bank offers to commercial and consumer clients?
- answer: A broad offering of deposit and lending products.
- source_doc: e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf p.12 chunk `c11866753bb3dbc2bf4ce346afc745d48c47a9f2`: The Bank operates as a regional bank providing a broad offering of deposit and lending products to commercial and consumer clients. The Bank's branches are strategically located in Kansas, Missouri, Oklahoma, Texas, Arizona, Colorado and New Mexico. Our approach to banking starts with our extraordinary service commitment. Our approach is highly tailored to our clients with the ability to customize products and services to meet our clients' individual needs. In addition to our branch locations, we also offer private banking solutions and commercial banking solutions. Private banking services
- notes: Direct CrossFirst business-model fact.

### q056

- question: Which Mercia portfolio company benefited from a $35 million investment from Aonic?
- answer: nDreams.
- source_doc: ac9aa244462c80705c3ff046542c02c459989742.pdf
- difficulty: medium
- requires_rewrite: True
- requires_multi_hop: False
- evidence excerpt:
  - ac9aa244462c80705c3ff046542c02c459989742.pdf p.29 chunk `4bcedc2a863e9f24f486993fc02e5ac146678aae`: The accelerated growth of nDreams continues in terms of both product releases and revenue, with this year's highlight being Mark Zuckerberg announcing the acclaimed Ghostbuster VR video game coming to Meta Quest 2 as a collaboration between nDreams, Ghost Corps and Sony Pictures Virtual Reality. During the year, nDreams also benefited from a $35million investment from the Swedish games studio group Aonic, adding £6.7million of fair value movement for Mercia's 33.2% direct holding stake.
- notes: Question uses portfolio-company wording; evidence names nDreams and Aonic.

### q057

- question: What was the name of the bank CrossFirst completed acquiring in 2022?
- answer: Farmers & Stockmens Bank ('Central').
- source_doc: e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf p.39 chunk `cb23672a0dcbe6fdbf022baf5e73e2ef5bee67de`: 2022 Highlights: Completed the acquisition of Farmers & Stockmens Bank ('Central') adding liquidity, new production talent, and expanding into attractive and growing markets o Added $389 million of loans and $570 million of deposits Total assets were $6.6 billion primarily made up of $5.4 billion in loans and $687 million in securities Loans grew $1.1 billion for the year or 26%; excluding the Central acquisition, loans grew 17% for the year Deposits grew $968 million for the year or 21%; excluding the Central acquisition, deposits grew 9% for the year
- notes: Direct acquisition-name fact.

### q058

- question: What two revenue streams does Yellow Pages say its revenues consist of?
- answer: Digital and print revenues.
- source_doc: 9d7a72445aba6860402c3acce75af02dc045f74d.pdf
- difficulty: medium
- requires_rewrite: True
- requires_multi_hop: False
- evidence excerpt:
  - 9d7a72445aba6860402c3acce75af02dc045f74d.pdf p.10 chunk `4e68e60d66398f40fe7486cca1d87864877738ad`: The decline rates for total revenues, digital revenues and print revenues all significantly improved year-over-year. Total revenue decline of 6.7% this year compares to a decline of 13.8% reported last year. Digital revenue decline of 5.6% this year compares to a decline of 12.2% reported last year. Print revenue decline of 10.6% this year compares to a decline of 18.6% reported last year. These improvements were due to better spend per customer in digital, increased renewal rates as well as improvement in customer claims. The improved spend per customer is due in part to increased pricing.
- notes: Uses revenue-stream wording; evidence discusses digital revenues and print revenues.

### q059

- question: What did Tradition say clients benefit from when placing orders?
- answer: Anonymity that reduces the market impact of placing orders.
- source_doc: 2779336b845a41544348abb7b3e6e5bd2ff893a2.pdf
- difficulty: medium
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - 2779336b845a41544348abb7b3e6e5bd2ff893a2.pdf p.14 chunk `30d03d92c6638ea587d61ec742aca3bc99866518`: Our clients have access to a global network, in-depth market intelligence, specialised knowledge of local markets and products, and large pools of liquidity. They benefit from the anonymity that reduces the market impact of placing orders. For this, brokers are organised in around 300 different desks, each representing a centre of expertise in a given market segment. Operating on the basis of a pure agency model with no conflict of interest and no position taking, our revenues primarily consist of commissions earned by matching trades, and only if a trade is matched.
- notes: Direct fact from Tradition's operating-model description.

### q060

- question: Which Holley facilities were many full-time employees based around?
- answer: The Bowling Green, KY headquarters, distribution center and manufacturing plants.
- source_doc: 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf p.10 chunk `248f9d61c2bbd7d00804948fd9cb0f6752cbcba8`: Holley's employees are integral to our strategic growth and success. We consider our team members to be our most valuable asset and seek to attract and maintain the highest quality talent by offering competitive benefits and wellness services, opportunities to grow professionally, and regular evaluations, among other initiatives. As of December 31, 2022, we employed 1,622 full-time employees and 100 temporary employees. Approximately 48% of our full-time employees are based primarily in our Bowling Green, KY headquarters, distribution center and manufacturing plants. None of our employees are
- notes: Direct Holley employee-location fact.

## numerical

### q011

- question: As of December 31, 2022, how many full-time and temporary employees did Holley employ?
- answer: 1,622 full-time employees and 100 temporary employees.
- source_doc: 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf p.10 chunk `248f9d61c2bbd7d00804948fd9cb0f6752cbcba8`: Holley's employees are integral to our strategic growth and success. We consider our team members to be our most valuable asset and seek to attract and maintain the highest quality talent by offering competitive benefits and wellness services, opportunities to grow professionally, and regular evaluations, among other initiatives. As of December 31, 2022, we employed 1,622 full-time employees and 100 temporary employees. Approximately 48% of our full-time employees are based primarily in our Bowling Green, KY headquarters, distribution center and manufacturing plants. None of our employees are
- notes: Explicit headcount figures; no unit conversion is needed.

### q012

- question: What were Tradition's underlying operating profitability margins for 2022 and 2021?
- answer: 12.7% in 2022 and 10.5% in 2021.
- source_doc: 2779336b845a41544348abb7b3e6e5bd2ff893a2.pdf
- difficulty: medium
- requires_rewrite: True
- requires_multi_hop: False
- evidence excerpt:
  - 2779336b845a41544348abb7b3e6e5bd2ff893a2.pdf p.4 chunk `fc41c61558edabc7bf70be96b9efa3a323263226`: Adjusted underlying operating profit was CHF 130.3m against CHF 99.9m in 2021, an increase of 34.0% at constant exchange rates, with an operating margin of 12.7% and 10.5% respectively. Consolidated net profit was CHF 97.4m compared with CHF 71.5m in 2021 with a Group share of CHF 89.1m against CHF 65.3m in 2021, an increase of 40.3% at constant exchange rates.
- notes: Question says profitability margins while evidence says operating margin; no unit conversion is needed.

### q013

- question: What were Holley's net sales for 2022 and 2021?
- answer: $688.4 million in 2022 and $692.9 million in 2021.
- source_doc: 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf p.36 chunk `f41d3c099381a2cbdc2076e170ab8463adb2ebd0`: Net sales for the year ended December 31, 2022, decreased $4.4 million, or 0.6%, to $688.4 million compared to $692.9 million for the year ended December 31, 2021. Non-comparable sales associated with acquisitions contributed $31.3 million to net sales in 2022, or year-over-year growth of 4.5%. The remaining comparable sales decreased by $35.7 million, or 5.2%. The decline in comparable sales was primarily driven by supply chain constraints that prevented the Company from building and shipping to orders received from customers and stabilizing demand due to a reduction in disposable income of
- notes: Financial amount question with explicit dollars and years; no unit conversion is needed.

### q014

- question: What total revenues did Yellow Pages report for 2022 versus 2021?
- answer: $268.3 million in 2022 compared with $287.6 million in 2021.
- source_doc: 9d7a72445aba6860402c3acce75af02dc045f74d.pdf
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - 9d7a72445aba6860402c3acce75af02dc045f74d.pdf p.10 chunk `ae2307117b36bcc67e2806ca6a83edf26a746bca`: Fiscal year 2022 versus 2021 Revenues (In thousands of Canadian dollars, except percentage information) Total revenues for the year ended December 31, 2022 decreased by 6.7% to $268.3 million, as compared to $287.6 million for the same period last year. The decrease in revenues is mainly due to the decline of our higher margin digital media and print products and to a lesser extent to our lower margin digital services products, thereby creating pressure on our gross profit margins.
- notes: Financial amount question in Canadian dollars; no unit conversion is needed.

### q015

- question: What profit before taxation and net assets did Mercia report in its 2022 highlights?
- answer: £27.4m profit before taxation and £200.6m net assets.
- source_doc: ac9aa244462c80705c3ff046542c02c459989742.pdf
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - ac9aa244462c80705c3ff046542c02c459989742.pdf p.38 chunk `b8245386d41dbf0e7d7d864ba8533a13e5a344a1`: 36 Mercia Asset Management PLC Annual Report & Accounts 2022 Chief Financial Officer's review Robust results and business fundamentals Chief Financial Officer Martin Glanfield 'Mercia has generated over £60million of pre-tax profits during the last two years.' 2022 Highlights £27.4m Profit before taxation 2021: £34.0m £200.6m Net assets 2021: £176.0m 45.6p Net assets per share 2021: 40.0p £61.3m Cash* 2021: £54.7m Including short-term liquidity investments growth
- notes: Mercia numerical highlight; no unit conversion is needed.

### q016

- question: What was Mercia's direct investment portfolio value as at 31 March 2022 and the 2021 comparator?
- answer: £119.6 million in 2022, compared with £96.2 million in 2021.
- source_doc: ac9aa244462c80705c3ff046542c02c459989742.pdf
- difficulty: medium
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - ac9aa244462c80705c3ff046542c02c459989742.pdf p.18 chunk `ff91bd2abbe86fb4a63313797b8e897ad8445bf0`: As at 31 March 2022, the value of the Group's direct investment portfolio was £119.6million (2021: £96.2million). This reflects an upward fair value movement of £11.4million (2021: £10.1million) and net cash invested of £18.4million (2021: £15.4million), less the realisation of Faradion, which accounted for £5.7million of the total opening portfolio fair value.
- notes: Mercia portfolio valuation with explicit date and comparator; no unit conversion is needed.

### q017

- question: What adjusted net income and adjusted diluted EPS did CrossFirst report for 2022?
- answer: $68.6 million in adjusted net income and adjusted diluted earnings per share of $1.37.
- source_doc: e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf
- difficulty: medium
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf p.3 chunk `9d6a0096586367fb79def8184c5bb904b5f0138d`: In terms of 2022 financial performance, we reported $68.6 million in adjusted net income (1) for the year, or adjusted diluted earnings per share of $1.37 (1) . We also grew loans by 26% for the year, with 17% of that growth being organic, and demand deposits grew from 13% to 25% of total deposits. When we look back to our initial public offering in August 2019, and all that has happened at the Bank and to our industry and country since, I am incredibly proud of the progress we have made. We have worked hard to deploy the capital we raised during the IPO through organic balance sheet growth,
- notes: CrossFirst financial-performance numbers; no unit conversion is needed.

### q018

- question: By how much did Yellow Pages' Adjusted EBITDA change, and what was the 2022 Adjusted EBITDA amount?
- answer: Adjusted EBITDA decreased by $5.4 million, or 5.3%, to $96.6 million.
- source_doc: 9d7a72445aba6860402c3acce75af02dc045f74d.pdf
- difficulty: medium
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - 9d7a72445aba6860402c3acce75af02dc045f74d.pdf p.11 chunk `7cffeaffd566e371a924e9da8c93a671ad02a2ed`: For the year ended December 31, 2022 Adjusted EBITDA decreased by $5.4 million or 5.3% to $96.6 million, compared to $102.0 million for the same period last year. The adjusted EBITDA margin increased during the year ended December 31, 2022 to 36.0%, compared to 35.5% for the same period last year. The decrease in Adjusted EBITDA for the year ended December 31, 2022, is the result of revenue pressures as well as ongoing investments in our tele-sales force capacity, partially offset by price increases, the efficiencies from optimization in cost of sales, reductions in other operating costs
- notes: Numeric metric includes amount, percentage change, and resulting value; no unit conversion is needed.

### q019

- question: What cash dividend per share did Tradition's Board seek approval to pay?
- answer: CHF 5.50 per share.
- source_doc: 2779336b845a41544348abb7b3e6e5bd2ff893a2.pdf
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - 2779336b845a41544348abb7b3e6e5bd2ff893a2.pdf p.4 chunk `3c186922691786e5c549fc0324fa4be614b0bf2a`: At the Annual General Meeting to be held on 25 May 2023, the Board will be seeking shareholder approval to pay a cash dividend of CHF 5.50 per share. In addition, an exceptional distribution of treasury shares will also be proposed, with one share to be distributed for every 100 shares held. I would like to thank all the Group's employees for their hard work and commitment throughout the year, and our shareholders for their continued loyalty and trust. Patrick Combes Key Figures
- notes: Dividend amount question; no unit conversion is needed.

### q020

- question: What voluntary contribution did Yellow Pages advance to its Defined Benefit Pension Plan wind-up deficit?
- answer: $24.0 million.
- source_doc: 9d7a72445aba6860402c3acce75af02dc045f74d.pdf
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - 9d7a72445aba6860402c3acce75af02dc045f74d.pdf p.3 chunk `3b203ae1c1828ca96830a6bad6f1f2217a421df1`: Cash to Shareholders and to Pension Plan. Pursuant to a statutory plan of arrangement, during 2022, we distributed $100.0 million to shareholders by way of a share repurchase from all shareholders on a pro rata basis and advanced $24.0 million of voluntary contributions to our Defined Benefit Pension Plan's wind-up deficit, in addition to our $4.0 million voluntary incremental payments as announced in May 2021 toward our Defined Benefit Pension Plan's wind-up deficit.
- notes: Pension contribution amount; no unit conversion is needed.

### q061

- question: What were Holley's gross profit and gross margin for 2022?
- answer: $253.7 million gross profit and 36.8% gross margin.
- source_doc: 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf
- difficulty: medium
- requires_rewrite: True
- requires_multi_hop: False
- evidence excerpt:
  - 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf p.37 chunk `9db8cf9d8c657d77d473f680a2c8ad69cbaeeb46`: Gross profit for the year ended December 31, 2022, decreased $33.2 million, or 11.6%, to $253.7 million compared to $286.8 million for the year ended December 31, 2021. Gross margin for the year ended December 31, 2022, of 36.8% decreased from gross margin of 41.4% for the year ended December 31, 2021. The decrease in gross profit and gross profit margin was driven primarily by inflationary factors, higher expenses associated with product rationalization and warranty costs, and a shift in the mix of products sold towards products with lower margins due in part to limitations caused by supply
- notes: Metric-specific numeric item; asks for gross profit and gross margin, not net sales.

### q062

- question: What was Holley's cost of goods sold for 2022 and the 2021 comparison?
- answer: $434.8 million in 2022 compared to $406.0 million in 2021.
- source_doc: 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf
- difficulty: medium
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf p.36 chunk `b49a1c1a0c325d83fc87db29b516b2fc7251b6ee`: Cost of Goods Sold Cost of goods sold for year ended December 31, 2022, increased $28.7 million, or 7.1%, to $434.8 million compared to $406.0 million for the year ended December 31, 2021. The increase in cost of goods sold during the year ended December 31, 2022, in which sales declined reflects compression in gross profit margin due to manufacturing inefficiencies driven by supply chain constraints, higher product rationalization charges, higher warranty costs, and inflationary pressures on certain other costs. 35
- notes: Wrong-metric distractor for sales/profit; no unit conversion is needed.

### q063

- question: What cash did Holley say it paid for the three 2022 acquisitions, net of cash acquired?
- answer: $14,863, as stated in the acquisition note.
- source_doc: 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf
- difficulty: hard
- requires_rewrite: True
- requires_multi_hop: False
- evidence excerpt:
  - 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf p.64 chunk `b2c9fc1e1b05c48a6ee76cd13177cc82b2891f19`: In 2022, the Company acquired substantially all the assets of John's Ind., Inc. ("John's"), Southern Kentucky Classics ("SKC"), and Vesta Motorsports USA, Inc., doing business as RaceQuip ("RaceQuip"). These acquisitions were immaterial business combinations. Cash paid for the three acquisitions, net of cash acquired, was $14,863, and was funded with borrowings from the Company's credit facility and cash on hand. The acquisitions resulted in both amortizable and nonamortizable intangibles and goodwill totaling $9,618. The goodwill and intangibles generated as a result of
- notes: Accounting-note numeric item with possible unit ambiguity; answer preserves the stated figure.

### q064

- question: What adjusted consolidated revenue did Tradition report for 2022 and 2021?
- answer: CHF 1,028.6m in 2022 compared with CHF 950.8m in 2021.
- source_doc: 2779336b845a41544348abb7b3e6e5bd2ff893a2.pdf
- difficulty: medium
- requires_rewrite: True
- requires_multi_hop: False
- evidence excerpt:
  - 2779336b845a41544348abb7b3e6e5bd2ff893a2.pdf p.4 chunk `ad8372bdc253202eb4152f60f8bdba250328e6df`: developments in 2023. This political and economic environment drove higher levels of activity in the financial markets from the second half of the year. Against this backdrop, the Group's adjusted consolidated revenue for the full year was up 10.6% at constant exchange rates to CHF 1,028.6m, compared with CHF 950.8m in 2021. After an increase of 7.7% at constant exchange rates in the first half, consolidated adjusted revenue was up 13.8% at constant exchange rates in the second half compared to the same period in 2021.
- notes: Metric/year ambiguity: asks adjusted consolidated revenue, not profit.

### q065

- question: What adjusted revenue did Tradition report for IDB and non-IDB activity?
- answer: CHF 994.7m for IDB and CHF 33.9m for non-IDB.
- source_doc: 2779336b845a41544348abb7b3e6e5bd2ff893a2.pdf
- difficulty: hard
- requires_rewrite: True
- requires_multi_hop: False
- evidence excerpt:
  - 2779336b845a41544348abb7b3e6e5bd2ff893a2.pdf p.42 chunk `46284b4497fece19b31d40ef7db4e4a7d18ed6f7`: Operating Review Against this backdrop, the Group's adjusted consolidated revenue was up 10.6% at constant exchange rates to CHF 1,028.6m, compared with CHF 950.8m in 2021. Adjusted revenue from interdealer broking business (IDB) grew 10.4% at constant exchange rates to CHF 994.7m, while revenue from the online forex trading business for retail investors in Japan (non-IDB), was ahead 14.6% to CHF 33.9m. At current exchange rates, adjusted consolidated revenue was up 8.2%, while IDB and non-IDB activity was up 8.5% and 0.3% respectively, caused by depreciation of JPY over the year.
- notes: Uses IDB/non-IDB aliases from the evidence; no currency conversion is needed.

### q066

- question: What were Yellow Pages' 2022 total, digital, and print revenue decline rates?
- answer: Total revenue declined 6.7%, digital revenue declined 5.6%, and print revenue declined 10.6%.
- source_doc: 9d7a72445aba6860402c3acce75af02dc045f74d.pdf
- difficulty: hard
- requires_rewrite: True
- requires_multi_hop: False
- evidence excerpt:
  - 9d7a72445aba6860402c3acce75af02dc045f74d.pdf p.10 chunk `4e68e60d66398f40fe7486cca1d87864877738ad`: The decline rates for total revenues, digital revenues and print revenues all significantly improved year-over-year. Total revenue decline of 6.7% this year compares to a decline of 13.8% reported last year. Digital revenue decline of 5.6% this year compares to a decline of 12.2% reported last year. Print revenue decline of 10.6% this year compares to a decline of 18.6% reported last year. These improvements were due to better spend per customer in digital, increased renewal rates as well as improvement in customer claims. The improved spend per customer is due in part to increased pricing.
- notes: Metric ambiguity among total, digital, and print revenue decline rates.

### q067

- question: How many common shares did Yellow Pages repurchase under the arrangement, and at what price per share?
- answer: 7,949,125 common shares at $12.58 per share.
- source_doc: 9d7a72445aba6860402c3acce75af02dc045f74d.pdf
- difficulty: medium
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - 9d7a72445aba6860402c3acce75af02dc045f74d.pdf p.20 chunk `8b11152e53365ebb60d37ef58304554cbce840cf`: Arrangement on September 27, 2022. On October 4, 2022, the Company repurchased from shareholders pro rata an aggregate of 7,949,125 common shares (including 388,082 shares held in treasury) at a purchase price of $12.58 per share pursuant to the Arrangement for a total of $101.0 million, including $1.0 million of transaction costs. The $101.0 million cash outlay was reduced by $4.9 million for the cancellation of 388,082 of YP's 1,298,994 shares held in Treasury for a net cash outlay of $96.1 million. Also pursuant to the Arrangement, the Company
- notes: Share-count and per-share-price numeric item.

### q068

- question: What net assets per share and cash did Mercia report in its 2022 CFO highlights?
- answer: 45.6p net assets per share and £61.3m cash.
- source_doc: ac9aa244462c80705c3ff046542c02c459989742.pdf
- difficulty: medium
- requires_rewrite: True
- requires_multi_hop: False
- evidence excerpt:
  - ac9aa244462c80705c3ff046542c02c459989742.pdf p.38 chunk `b8245386d41dbf0e7d7d864ba8533a13e5a344a1`: 36 Mercia Asset Management PLC Annual Report & Accounts 2022 Chief Financial Officer's review Robust results and business fundamentals Chief Financial Officer Martin Glanfield 'Mercia has generated over £60million of pre-tax profits during the last two years.' 2022 Highlights £27.4m Profit before taxation 2021: £34.0m £200.6m Net assets 2021: £176.0m 45.6p Net assets per share 2021: 40.0p £61.3m Cash* 2021: £54.7m Including short-term liquidity investments growth
- notes: Metric-specific Mercia numeric item; asks for per-share NAV and cash.

### q069

- question: What return multiple and IRR did Mercia report for its Faradion direct holding?
- answer: A 4.4x return and a c.72% internal rate of return.
- source_doc: ac9aa244462c80705c3ff046542c02c459989742.pdf
- difficulty: medium
- requires_rewrite: True
- requires_multi_hop: False
- evidence excerpt:
  - ac9aa244462c80705c3ff046542c02c459989742.pdf p.18 chunk `9eb8d2808502531479f262a468b101e6dcfc400f`: Faradion was sold in January 2022 to India's Reliance New Energy Solar Ltd, a wholly owned subsidiary of India-based Reliance Industries Ltd, for £100.0million. Total cash proceeds back to Mercia's balance sheet of £19.4million resulted in a realised gain of £9.9million, generating a 4.4x return on Mercia's direct investment cost of £4.4million and a c.72% internal rate of return ('IRR') since the first direct investment in 2017.
- notes: Uses return shorthand and IRR alias; no unit conversion is needed.

### q070

- question: From 2019 to 2022, what did CrossFirst say its net interest margin improved from and to?
- answer: From 3.32% in 2019 to 3.50% in 2022.
- source_doc: e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf
- difficulty: medium
- requires_rewrite: True
- requires_multi_hop: False
- evidence excerpt:
  - e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf p.3 chunk `da118e59c27fe9af087228b1d79469605862e13d`: We have grown our balance sheet by $1.7 billion or over 33% Demand deposits have grown from 13% to 25% of total deposits Net Interest Margin - Fully Tax Equivalent ('FTE') (1) has improved from 3.32% for 2019 to 3.50% for 2022 Credit quality has substantially improved with our non-performing assets ratio declining from 0.97% as of the end of 2019 to only 0.20% as of the end of 2022 Operating revenue has grown to $211 million in 2022 . That is an increase of $61 million or more than 40% from our total operating revenue in 2019
- notes: Year-specific metric question; asks NIM/FTE rather than revenue.

## multi_hop

### q021

- question: What evidence shows Holley was both a broad brand portfolio company and a sizable employer at the end of 2022?
- answer: Holley's portfolio had over 70 brands across 30 product categories, and it employed 1,622 full-time employees plus 100 temporary employees as of December 31, 2022.
- source_doc: 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf
- difficulty: medium
- requires_rewrite: True
- requires_multi_hop: True
- evidence excerpt:
  - 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf p.7 chunk `511a4a9c6a50d200b21c84f7d683ae7f91993183`: Brands We have a strong portfolio of brands covering various product categories. Our portfolio consists of over 70 brands spanning across 30 product categories. Our top seven brands generated 68% of our sales in 2022. Holley EFI : Currently our largest brand and represented 14% of our sales for 2022. Our Holley EFI brand focuses on electronic fuel injection technology and showcases our new product development engine.
  - 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf p.10 chunk `248f9d61c2bbd7d00804948fd9cb0f6752cbcba8`: Holley's employees are integral to our strategic growth and success. We consider our team members to be our most valuable asset and seek to attract and maintain the highest quality talent by offering competitive benefits and wellness services, opportunities to grow professionally, and regular evaluations, among other initiatives. As of December 31, 2022, we employed 1,622 full-time employees and 100 temporary employees. Approximately 48% of our full-time employees are based primarily in our Bowling Green, KY headquarters, distribution center and manufacturing plants. None of our employees are
- notes: Combines Holley's brand portfolio scale and employee headcount from two chunks/pages.

### q022

- question: Which acquisition expanded CrossFirst in 2022, and what adjusted diluted EPS and adjusted ROE did CrossFirst report for that year?
- answer: CrossFirst completed the acquisition of Farmers & Stockmens Bank ('Central'); for the year it delivered $1.37 in adjusted diluted earnings per share and adjusted ROE improved to 11.11% in 2022.
- source_doc: e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf
- difficulty: hard
- requires_rewrite: True
- requires_multi_hop: True
- evidence excerpt:
  - e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf p.39 chunk `cb23672a0dcbe6fdbf022baf5e73e2ef5bee67de`: 2022 Highlights: Completed the acquisition of Farmers & Stockmens Bank ('Central') adding liquidity, new production talent, and expanding into attractive and growing markets o Added $389 million of loans and $570 million of deposits Total assets were $6.6 billion primarily made up of $5.4 billion in loans and $687 million in securities Loans grew $1.1 billion for the year or 26%; excluding the Central acquisition, loans grew 17% for the year Deposits grew $968 million for the year or 21%; excluding the Central acquisition, deposits grew 9% for the year
  - e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf p.2 chunk `be6c031317d23964e1e8adfd8f0c0e2832b95bb8`: 2022 Highlights Since 2019, we grew our balance sheet by $1.7 billion or over 33% BILLION $ 6.6 TOTAL ASSETS for the year or 26% (excluding the Central acquisition, loans grew 17% for the year) BILLION $ 1 . 1 LOANS GREW MILLION $ 68.6 for the year, delivering $1.37 in adjusted diluted earnings per share (1) ADJUSTED NET INCOME (1) Adjusted ROE improved from 5.18% in 2019 to 11.11% in 2022 11 . 11 % ADJUSTED RETURN ON COMMON EQUITY (ROE) (1) for the year or 21% (excluding the 9% for the year) Central acquisition, deposits grew MILLION $ 968 DEPOSITS GREW
- notes: Uses one chunk for the acquisition and another for adjusted EPS/ROE.

### q023

- question: How did Mercia's Faradion exit relate to the reported value of its direct investment portfolio?
- answer: Mercia sold Faradion in January 2022 for £100.0 million, generating £19.4 million of cash proceeds to Mercia's balance sheet; as at 31 March 2022, the Group's direct investment portfolio was valued at £119.6 million.
- source_doc: ac9aa244462c80705c3ff046542c02c459989742.pdf
- difficulty: hard
- requires_rewrite: True
- requires_multi_hop: True
- evidence excerpt:
  - ac9aa244462c80705c3ff046542c02c459989742.pdf p.18 chunk `9eb8d2808502531479f262a468b101e6dcfc400f`: Faradion was sold in January 2022 to India's Reliance New Energy Solar Ltd, a wholly owned subsidiary of India-based Reliance Industries Ltd, for £100.0million. Total cash proceeds back to Mercia's balance sheet of £19.4million resulted in a realised gain of £9.9million, generating a 4.4x return on Mercia's direct investment cost of £4.4million and a c.72% internal rate of return ('IRR') since the first direct investment in 2017.
  - ac9aa244462c80705c3ff046542c02c459989742.pdf p.18 chunk `ff91bd2abbe86fb4a63313797b8e897ad8445bf0`: As at 31 March 2022, the value of the Group's direct investment portfolio was £119.6million (2021: £96.2million). This reflects an upward fair value movement of £11.4million (2021: £10.1million) and net cash invested of £18.4million (2021: £15.4million), less the realisation of Faradion, which accounted for £5.7million of the total opening portfolio fair value.
- notes: Mercia multi-hop across exit proceeds and portfolio valuation chunks.

### q024

- question: What shareholder cash action did Yellow Pages take in 2022, and what was the net cash outlay after treasury-share cancellation?
- answer: Yellow Pages distributed $100.0 million to shareholders by way of a share repurchase; the arrangement had a net cash outlay of $96.1 million after reducing the $101.0 million cash outlay by $4.9 million for treasury-share cancellation.
- source_doc: 9d7a72445aba6860402c3acce75af02dc045f74d.pdf
- difficulty: hard
- requires_rewrite: True
- requires_multi_hop: True
- evidence excerpt:
  - 9d7a72445aba6860402c3acce75af02dc045f74d.pdf p.3 chunk `3b203ae1c1828ca96830a6bad6f1f2217a421df1`: Cash to Shareholders and to Pension Plan. Pursuant to a statutory plan of arrangement, during 2022, we distributed $100.0 million to shareholders by way of a share repurchase from all shareholders on a pro rata basis and advanced $24.0 million of voluntary contributions to our Defined Benefit Pension Plan's wind-up deficit, in addition to our $4.0 million voluntary incremental payments as announced in May 2021 toward our Defined Benefit Pension Plan's wind-up deficit.
  - 9d7a72445aba6860402c3acce75af02dc045f74d.pdf p.20 chunk `8b11152e53365ebb60d37ef58304554cbce840cf`: Arrangement on September 27, 2022. On October 4, 2022, the Company repurchased from shareholders pro rata an aggregate of 7,949,125 common shares (including 388,082 shares held in treasury) at a purchase price of $12.58 per share pursuant to the Arrangement for a total of $101.0 million, including $1.0 million of transaction costs. The $101.0 million cash outlay was reduced by $4.9 million for the cancellation of 388,082 of YP's 1,298,994 shares held in Treasury for a net cash outlay of $96.1 million. Also pursuant to the Arrangement, the Company
- notes: Uses the high-level shareholder distribution chunk plus arrangement details for the net cash outlay.

### q025

- question: What did Tradition report about operating profitability and shareholder distributions for the year?
- answer: Tradition reported adjusted underlying operating profit of CHF 130.3m with an operating margin of 12.7%, and the Board sought approval for a CHF 5.50 per share cash dividend plus one treasury share for every 100 shares held.
- source_doc: 2779336b845a41544348abb7b3e6e5bd2ff893a2.pdf
- difficulty: hard
- requires_rewrite: True
- requires_multi_hop: True
- evidence excerpt:
  - 2779336b845a41544348abb7b3e6e5bd2ff893a2.pdf p.4 chunk `fc41c61558edabc7bf70be96b9efa3a323263226`: Adjusted underlying operating profit was CHF 130.3m against CHF 99.9m in 2021, an increase of 34.0% at constant exchange rates, with an operating margin of 12.7% and 10.5% respectively. Consolidated net profit was CHF 97.4m compared with CHF 71.5m in 2021 with a Group share of CHF 89.1m against CHF 65.3m in 2021, an increase of 40.3% at constant exchange rates.
  - 2779336b845a41544348abb7b3e6e5bd2ff893a2.pdf p.4 chunk `3c186922691786e5c549fc0324fa4be614b0bf2a`: At the Annual General Meeting to be held on 25 May 2023, the Board will be seeking shareholder approval to pay a cash dividend of CHF 5.50 per share. In addition, an exceptional distribution of treasury shares will also be proposed, with one share to be distributed for every 100 shares held. I would like to thank all the Group's employees for their hard work and commitment throughout the year, and our shareholders for their continued loyalty and trust. Patrick Combes Key Figures
- notes: Combines operating profitability and shareholder distribution evidence.

### q026

- question: How do Holley's founding history and 2022 acquisition activity describe the company's automotive aftermarket strategy?
- answer: Holley was founded in 1903 and describes itself as a designer, marketer, and manufacturer of high-performance automotive aftermarket products; it also added to its brand lineup through 2022 acquisitions including John's, SKC, and RaceQuip.
- source_doc: 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf
- difficulty: medium
- requires_rewrite: True
- requires_multi_hop: True
- evidence excerpt:
  - 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf p.5 chunk `506c552e1d504118617d1722e8e47503db17fd21`: Founded in 1903, Holley, Inc. ('Holley' or the 'Company') has been a part of the automotive industry for well over a century. We are a leading designer, marketer, and manufacturer of high-performance automotive aftermarket products for car and truck enthusiasts. Our products span a number of automotive platforms and are sold across multiple channels. We attribute a major component of our success to our brands, including 'Holley', 'APR', 'MSD' and 'Flowmaster', among others. In addition, we have recently added to our brand lineup through a series of strategic acquisitions, including our 2022
  - 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf p.5 chunk `f0e0e2b2d073c0a6ee3a7b2b38b852c13178f23e`: our brand lineup through a series of strategic acquisitions, including our 2022 acquisitions of substantially all the assets of John's Ind., Inc. ('John's'), Southern Kentucky Classics ('SKC'), and Vesta Motorsports USA, Inc., d.b.a. RaceQuip ('RaceQuip'), our 2021 acquisitions of substantially all the assets of AEM Performance Electronics ('AEM'), Classic Instruments LLC ('Classic Instruments'), ADS Precision Machining, Inc., d.b.a. Arizona Desert Shocks ('ADS'), Baer, Inc, d.b.a. Baer Brakes ('Baer'), Brothers Mail Order Industries, Inc., d.b.a. Brothers Trucks
- notes: Combines company background and acquisition activity from two Holley chunks.

### q027

- question: What evidence connects Mercia's UK-only investment focus with its ESG-related operating milestone?
- answer: Mercia states that it invests exclusively in the UK and also says it measured and offset its carbon footprint to become a carbon-neutral company.
- source_doc: ac9aa244462c80705c3ff046542c02c459989742.pdf
- difficulty: medium
- requires_rewrite: False
- requires_multi_hop: True
- evidence excerpt:
  - ac9aa244462c80705c3ff046542c02c459989742.pdf p.14 chunk `4b0c168aab6493db6e430a3e4c4433356a76ef65`: £119.6m Value of direct investment portfolio See more on page 26. investees We invest exclusively in the UK Our teams are conveniently based in the following eight regional locations across the UK. Bristol Manchester Preston Leeds Newcastle Sheffield London Henley-in-Arden
  - ac9aa244462c80705c3ff046542c02c459989742.pdf p.5 chunk `60c160920af9ec76e2cd63915a26b3ce2e89818a`: There is always more that can be done, but it was encouraging to see that at our recent senior leadership strategy day, half of the 14 attendees were women. Equally encouraging is that despite it not yet being mandatory for Mercia, we have taken the proactive decision to measure and report on our carbon footprint - for the first time Mercia has been measured and offset its carbon footprint to become a carbon-neutral company. As part of our mantra of 'responsible investing with purpose', we believe in practising what we ask of our investee companies, in terms of both good governance and being
- notes: Mercia multi-hop over investment focus and ESG/carbon-neutral evidence from separate chunks.

### q028

- question: What evidence shows CrossFirst had both a multi-state branch footprint and improved deposit mix?
- answer: CrossFirst's branches were strategically located in Kansas, Missouri, Oklahoma, Texas, Arizona, Colorado and New Mexico, and demand deposits grew from 13% to 25% of total deposits.
- source_doc: e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf
- difficulty: medium
- requires_rewrite: True
- requires_multi_hop: True
- evidence excerpt:
  - e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf p.12 chunk `c11866753bb3dbc2bf4ce346afc745d48c47a9f2`: The Bank operates as a regional bank providing a broad offering of deposit and lending products to commercial and consumer clients. The Bank's branches are strategically located in Kansas, Missouri, Oklahoma, Texas, Arizona, Colorado and New Mexico. Our approach to banking starts with our extraordinary service commitment. Our approach is highly tailored to our clients with the ability to customize products and services to meet our clients' individual needs. In addition to our branch locations, we also offer private banking solutions and commercial banking solutions. Private banking services
  - e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf p.3 chunk `9d6a0096586367fb79def8184c5bb904b5f0138d`: In terms of 2022 financial performance, we reported $68.6 million in adjusted net income (1) for the year, or adjusted diluted earnings per share of $1.37 (1) . We also grew loans by 26% for the year, with 17% of that growth being organic, and demand deposits grew from 13% to 25% of total deposits. When we look back to our initial public offering in August 2019, and all that has happened at the Bank and to our industry and country since, I am incredibly proud of the progress we have made. We have worked hard to deploy the capital we raised during the IPO through organic balance sheet growth,
- notes: Combines geographic footprint and deposit mix from separate CrossFirst chunks.

### q029

- question: How did Yellow Pages describe both revenue pressure and profitability for 2022?
- answer: Yellow Pages reported total revenues decreased 6.7% to $268.3 million from $287.6 million, while Adjusted EBITDA decreased to $96.6 million and the adjusted EBITDA margin increased to 36.0%.
- source_doc: 9d7a72445aba6860402c3acce75af02dc045f74d.pdf
- difficulty: hard
- requires_rewrite: True
- requires_multi_hop: True
- evidence excerpt:
  - 9d7a72445aba6860402c3acce75af02dc045f74d.pdf p.10 chunk `ae2307117b36bcc67e2806ca6a83edf26a746bca`: Fiscal year 2022 versus 2021 Revenues (In thousands of Canadian dollars, except percentage information) Total revenues for the year ended December 31, 2022 decreased by 6.7% to $268.3 million, as compared to $287.6 million for the same period last year. The decrease in revenues is mainly due to the decline of our higher margin digital media and print products and to a lesser extent to our lower margin digital services products, thereby creating pressure on our gross profit margins.
  - 9d7a72445aba6860402c3acce75af02dc045f74d.pdf p.11 chunk `7cffeaffd566e371a924e9da8c93a671ad02a2ed`: For the year ended December 31, 2022 Adjusted EBITDA decreased by $5.4 million or 5.3% to $96.6 million, compared to $102.0 million for the same period last year. The adjusted EBITDA margin increased during the year ended December 31, 2022 to 36.0%, compared to 35.5% for the same period last year. The decrease in Adjusted EBITDA for the year ended December 31, 2022, is the result of revenue pressures as well as ongoing investments in our tele-sales force capacity, partially offset by price increases, the efficiencies from optimization in cost of sales, reductions in other operating costs
- notes: Combines revenue and profitability chunks to test synthesis under mixed signals.

### q030

- question: What evidence shows Mercia had both financial resources and an ESG-related operating milestone?
- answer: Mercia reported £61.3m of cash in its 2022 highlights and said it measured and offset its carbon footprint to become a carbon-neutral company.
- source_doc: ac9aa244462c80705c3ff046542c02c459989742.pdf
- difficulty: medium
- requires_rewrite: True
- requires_multi_hop: True
- evidence excerpt:
  - ac9aa244462c80705c3ff046542c02c459989742.pdf p.38 chunk `b8245386d41dbf0e7d7d864ba8533a13e5a344a1`: 36 Mercia Asset Management PLC Annual Report & Accounts 2022 Chief Financial Officer's review Robust results and business fundamentals Chief Financial Officer Martin Glanfield 'Mercia has generated over £60million of pre-tax profits during the last two years.' 2022 Highlights £27.4m Profit before taxation 2021: £34.0m £200.6m Net assets 2021: £176.0m 45.6p Net assets per share 2021: 40.0p £61.3m Cash* 2021: £54.7m Including short-term liquidity investments growth
  - ac9aa244462c80705c3ff046542c02c459989742.pdf p.5 chunk `60c160920af9ec76e2cd63915a26b3ce2e89818a`: There is always more that can be done, but it was encouraging to see that at our recent senior leadership strategy day, half of the 14 attendees were women. Equally encouraging is that despite it not yet being mandatory for Mercia, we have taken the proactive decision to measure and report on our carbon footprint - for the first time Mercia has been measured and offset its carbon footprint to become a carbon-neutral company. As part of our mantra of 'responsible investing with purpose', we believe in practising what we ask of our investee companies, in terms of both good governance and being
- notes: Combines Mercia financial highlight and ESG/carbon-neutral evidence.

### q071

- question: How do Holley's 2022 net sales and gross profit figures show different performance signals?
- answer: Holley's 2022 net sales were $688.4 million versus $692.9 million in 2021, while gross profit decreased to $253.7 million and gross margin was 36.8%.
- source_doc: 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf
- difficulty: hard
- requires_rewrite: True
- requires_multi_hop: True
- evidence excerpt:
  - 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf p.36 chunk `f41d3c099381a2cbdc2076e170ab8463adb2ebd0`: Net sales for the year ended December 31, 2022, decreased $4.4 million, or 0.6%, to $688.4 million compared to $692.9 million for the year ended December 31, 2021. Non-comparable sales associated with acquisitions contributed $31.3 million to net sales in 2022, or year-over-year growth of 4.5%. The remaining comparable sales decreased by $35.7 million, or 5.2%. The decline in comparable sales was primarily driven by supply chain constraints that prevented the Company from building and shipping to orders received from customers and stabilizing demand due to a reduction in disposable income of
  - 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf p.37 chunk `9db8cf9d8c657d77d473f680a2c8ad69cbaeeb46`: Gross profit for the year ended December 31, 2022, decreased $33.2 million, or 11.6%, to $253.7 million compared to $286.8 million for the year ended December 31, 2021. Gross margin for the year ended December 31, 2022, of 36.8% decreased from gross margin of 41.4% for the year ended December 31, 2021. The decrease in gross profit and gross profit margin was driven primarily by inflationary factors, higher expenses associated with product rationalization and warranty costs, and a shift in the mix of products sold towards products with lower margins due in part to limitations caused by supply
- notes: Cross-chunk metric comparison designed to avoid confusing revenue with gross profit.

### q072

- question: What did Tradition report for adjusted consolidated revenue and adjusted underlying operating profit?
- answer: Tradition reported adjusted consolidated revenue of CHF 1,028.6m and adjusted underlying operating profit of CHF 130.3m.
- source_doc: 2779336b845a41544348abb7b3e6e5bd2ff893a2.pdf
- difficulty: hard
- requires_rewrite: True
- requires_multi_hop: True
- evidence excerpt:
  - 2779336b845a41544348abb7b3e6e5bd2ff893a2.pdf p.4 chunk `ad8372bdc253202eb4152f60f8bdba250328e6df`: developments in 2023. This political and economic environment drove higher levels of activity in the financial markets from the second half of the year. Against this backdrop, the Group's adjusted consolidated revenue for the full year was up 10.6% at constant exchange rates to CHF 1,028.6m, compared with CHF 950.8m in 2021. After an increase of 7.7% at constant exchange rates in the first half, consolidated adjusted revenue was up 13.8% at constant exchange rates in the second half compared to the same period in 2021.
  - 2779336b845a41544348abb7b3e6e5bd2ff893a2.pdf p.4 chunk `fc41c61558edabc7bf70be96b9efa3a323263226`: Adjusted underlying operating profit was CHF 130.3m against CHF 99.9m in 2021, an increase of 34.0% at constant exchange rates, with an operating margin of 12.7% and 10.5% respectively. Consolidated net profit was CHF 97.4m compared with CHF 71.5m in 2021 with a Group share of CHF 89.1m against CHF 65.3m in 2021, an increase of 40.3% at constant exchange rates.
- notes: Combines revenue and profit metrics across chunks; useful for wrong-metric traps.

### q073

- question: How did Yellow Pages combine revenue decline with margin improvement in 2022?
- answer: Total revenues decreased 6.7% to $268.3 million, while the adjusted EBITDA margin increased to 36.0% from 35.5%.
- source_doc: 9d7a72445aba6860402c3acce75af02dc045f74d.pdf
- difficulty: hard
- requires_rewrite: True
- requires_multi_hop: True
- evidence excerpt:
  - 9d7a72445aba6860402c3acce75af02dc045f74d.pdf p.10 chunk `ae2307117b36bcc67e2806ca6a83edf26a746bca`: Fiscal year 2022 versus 2021 Revenues (In thousands of Canadian dollars, except percentage information) Total revenues for the year ended December 31, 2022 decreased by 6.7% to $268.3 million, as compared to $287.6 million for the same period last year. The decrease in revenues is mainly due to the decline of our higher margin digital media and print products and to a lesser extent to our lower margin digital services products, thereby creating pressure on our gross profit margins.
  - 9d7a72445aba6860402c3acce75af02dc045f74d.pdf p.11 chunk `7cffeaffd566e371a924e9da8c93a671ad02a2ed`: For the year ended December 31, 2022 Adjusted EBITDA decreased by $5.4 million or 5.3% to $96.6 million, compared to $102.0 million for the same period last year. The adjusted EBITDA margin increased during the year ended December 31, 2022 to 36.0%, compared to 35.5% for the same period last year. The decrease in Adjusted EBITDA for the year ended December 31, 2022, is the result of revenue pressures as well as ongoing investments in our tele-sales force capacity, partially offset by price increases, the efficiencies from optimization in cost of sales, reductions in other operating costs
- notes: Requires combining revenue pressure with EBITDA-margin improvement, a partial-evidence trap.

### q074

- question: What evidence shows Mercia had both realised cash from Faradion and fair-value movement from nDreams?
- answer: Mercia received £19.4 million of cash proceeds from Faradion and nDreams added £6.7 million of fair value movement for Mercia's 33.2% direct holding stake.
- source_doc: ac9aa244462c80705c3ff046542c02c459989742.pdf
- difficulty: hard
- requires_rewrite: True
- requires_multi_hop: True
- evidence excerpt:
  - ac9aa244462c80705c3ff046542c02c459989742.pdf p.18 chunk `9eb8d2808502531479f262a468b101e6dcfc400f`: Faradion was sold in January 2022 to India's Reliance New Energy Solar Ltd, a wholly owned subsidiary of India-based Reliance Industries Ltd, for £100.0million. Total cash proceeds back to Mercia's balance sheet of £19.4million resulted in a realised gain of £9.9million, generating a 4.4x return on Mercia's direct investment cost of £4.4million and a c.72% internal rate of return ('IRR') since the first direct investment in 2017.
  - ac9aa244462c80705c3ff046542c02c459989742.pdf p.29 chunk `4bcedc2a863e9f24f486993fc02e5ac146678aae`: The accelerated growth of nDreams continues in terms of both product releases and revenue, with this year's highlight being Mark Zuckerberg announcing the acclaimed Ghostbuster VR video game coming to Meta Quest 2 as a collaboration between nDreams, Ghost Corps and Sony Pictures Virtual Reality. During the year, nDreams also benefited from a $35million investment from the Swedish games studio group Aonic, adding £6.7million of fair value movement for Mercia's 33.2% direct holding stake.
- notes: Cross-chunk Mercia investment-performance synthesis.

### q075

- question: What evidence shows CrossFirst improved both margin and credit-quality metrics?
- answer: CrossFirst's net interest margin improved from 3.32% in 2019 to 3.50% in 2022, and its non-performing assets ratio declined from 0.97% at the end of 2019 to 0.20% at the end of 2022.
- source_doc: e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf
- difficulty: hard
- requires_rewrite: True
- requires_multi_hop: True
- evidence excerpt:
  - e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf p.42 chunk `393e7db192c96a749de4cfb6a2d133a6f314b4e2`: Net Interest Income Full year 2022 net interest income grew $24.8 million, an increase of 15% compared to 2021. Full year net interest income - FTE grew $25.1 million, an increase of 15% compared to 2021, while the net interest margin ('NIM') - FTE increased to 3.50% from 3.17% in the prior year due to the higher interest rate environment as well as the mix shift from cash into higher earning assets as noted above. The NIM - FTE also benefited from a 31% increase in non-interest-bearing deposits which benefited the NIM-FTE 4 basis points. We currently expect the net interest margin to remain
  - e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf p.3 chunk `da118e59c27fe9af087228b1d79469605862e13d`: We have grown our balance sheet by $1.7 billion or over 33% Demand deposits have grown from 13% to 25% of total deposits Net Interest Margin - Fully Tax Equivalent ('FTE') (1) has improved from 3.32% for 2019 to 3.50% for 2022 Credit quality has substantially improved with our non-performing assets ratio declining from 0.97% as of the end of 2019 to only 0.20% as of the end of 2022 Operating revenue has grown to $211 million in 2022 . That is an increase of $61 million or more than 40% from our total operating revenue in 2019
- notes: Combines NIM and NPA ratio from separate CrossFirst chunks; tests metric disambiguation.

### q076

- question: Which companies did Holley acquire in 2022, and how much cash was paid for the three acquisitions?
- answer: Holley acquired John's, SKC, and RaceQuip; cash paid for the three acquisitions, net of cash acquired, was $14,863.
- source_doc: 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf
- difficulty: hard
- requires_rewrite: True
- requires_multi_hop: True
- evidence excerpt:
  - 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf p.5 chunk `f0e0e2b2d073c0a6ee3a7b2b38b852c13178f23e`: our brand lineup through a series of strategic acquisitions, including our 2022 acquisitions of substantially all the assets of John's Ind., Inc. ('John's'), Southern Kentucky Classics ('SKC'), and Vesta Motorsports USA, Inc., d.b.a. RaceQuip ('RaceQuip'), our 2021 acquisitions of substantially all the assets of AEM Performance Electronics ('AEM'), Classic Instruments LLC ('Classic Instruments'), ADS Precision Machining, Inc., d.b.a. Arizona Desert Shocks ('ADS'), Baer, Inc, d.b.a. Baer Brakes ('Baer'), Brothers Mail Order Industries, Inc., d.b.a. Brothers Trucks
  - 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf p.64 chunk `b2c9fc1e1b05c48a6ee76cd13177cc82b2891f19`: In 2022, the Company acquired substantially all the assets of John's Ind., Inc. ("John's"), Southern Kentucky Classics ("SKC"), and Vesta Motorsports USA, Inc., doing business as RaceQuip ("RaceQuip"). These acquisitions were immaterial business combinations. Cash paid for the three acquisitions, net of cash acquired, was $14,863, and was funded with borrowings from the Company's credit facility and cash on hand. The acquisitions resulted in both amortizable and nonamortizable intangibles and goodwill totaling $9,618. The goodwill and intangibles generated as a result of
- notes: Combines acquisition names and accounting-note amount across chunks.

### q077

- question: What shareholder distributions did Tradition propose in both per-share and aggregate terms?
- answer: Tradition proposed a cash dividend of CHF 5.50 per share, estimated at CHF 40,781,000, plus one bonus share for every 100 shares held.
- source_doc: 2779336b845a41544348abb7b3e6e5bd2ff893a2.pdf
- difficulty: hard
- requires_rewrite: True
- requires_multi_hop: True
- evidence excerpt:
  - 2779336b845a41544348abb7b3e6e5bd2ff893a2.pdf p.4 chunk `3c186922691786e5c549fc0324fa4be614b0bf2a`: At the Annual General Meeting to be held on 25 May 2023, the Board will be seeking shareholder approval to pay a cash dividend of CHF 5.50 per share. In addition, an exceptional distribution of treasury shares will also be proposed, with one share to be distributed for every 100 shares held. I would like to thank all the Group's employees for their hard work and commitment throughout the year, and our shareholders for their continued loyalty and trust. Patrick Combes Key Figures
  - 2779336b845a41544348abb7b3e6e5bd2ff893a2.pdf p.143 chunk `8a1bf8dbd247873e4afb4669648999456bd47e9a`: At the Annual General Meeting to be held on 25 May 2023, the Board of Directors will be seeking shareholder approval for a cash dividend of CHF 5.50 per share to be paid from available earnings, for an estimated distribution of CHF 40,781,000 for the 2022 financial year on the share capital conferring entitlement to a dividend. No dividend is to be paid on treasury shares held by the Company on the payment date. The Board will also be seeking shareholder approval for the distribution of one bonus share for every 100 shares held to be paid from available earnings. If the Annual General Meeting
- notes: Cross-page shareholder distribution question with per-share and aggregate figures.

### q078

- question: What evidence shows Mercia had external fund awards and a strong cash position?
- answer: The British Business Bank awarded £31.4 million to Mercia's equity and debt funds, and Mercia reported £61.3m of cash in its CFO highlights.
- source_doc: ac9aa244462c80705c3ff046542c02c459989742.pdf
- difficulty: medium
- requires_rewrite: True
- requires_multi_hop: True
- evidence excerpt:
  - ac9aa244462c80705c3ff046542c02c459989742.pdf p.3 chunk `3e89fac0fc26b0ddce369677c80a82b532310549`: Annual Report & Accounts 2022 Mercia Asset Management PLC 1 Strategic report 2022 highlights Sale of Faradion Ltd with total proceeds of £19.4million £11.4million fair value movements ('FvM') in the direct investment portfolio, following continued commercial progress, including significant third-party investment into nDreams Operational highlights £31.4million awarded by the British Business Bank ('BBB') to Mercia's equity and debt funds c.£87million of cash returned to fund investors from successful realisations (2021: c.£27million)
  - ac9aa244462c80705c3ff046542c02c459989742.pdf p.38 chunk `b8245386d41dbf0e7d7d864ba8533a13e5a344a1`: 36 Mercia Asset Management PLC Annual Report & Accounts 2022 Chief Financial Officer's review Robust results and business fundamentals Chief Financial Officer Martin Glanfield 'Mercia has generated over £60million of pre-tax profits during the last two years.' 2022 Highlights £27.4m Profit before taxation 2021: £34.0m £200.6m Net assets 2021: £176.0m 45.6p Net assets per share 2021: 40.0p £61.3m Cash* 2021: £54.7m Including short-term liquidity investments growth
- notes: Combines operational funding highlight with balance-sheet cash.

### q079

- question: How did Yellow Pages' arrangement affect both shareholders and its pension plan?
- answer: Yellow Pages distributed $100.0 million to shareholders by share repurchase and advanced $24.0 million of voluntary contributions to its Defined Benefit Pension Plan's wind-up deficit.
- source_doc: 9d7a72445aba6860402c3acce75af02dc045f74d.pdf
- difficulty: medium
- requires_rewrite: True
- requires_multi_hop: True
- evidence excerpt:
  - 9d7a72445aba6860402c3acce75af02dc045f74d.pdf p.3 chunk `3b203ae1c1828ca96830a6bad6f1f2217a421df1`: Cash to Shareholders and to Pension Plan. Pursuant to a statutory plan of arrangement, during 2022, we distributed $100.0 million to shareholders by way of a share repurchase from all shareholders on a pro rata basis and advanced $24.0 million of voluntary contributions to our Defined Benefit Pension Plan's wind-up deficit, in addition to our $4.0 million voluntary incremental payments as announced in May 2021 toward our Defined Benefit Pension Plan's wind-up deficit.
  - 9d7a72445aba6860402c3acce75af02dc045f74d.pdf p.20 chunk `c1e7af954b65c77ae358a97c1369cd8a47f8af74`: net cash outlay of $96.1 million. Also pursuant to the Arrangement, the Company advanced $24.0 million to the Defined Benefit Pension Plan's (the 'Pension Plan') wind-up deficit for the year ended December 31, 2022 (refer to ' Pension Contributions ' section for additional details).
- notes: Combines shareholder and pension-plan consequences from separate arrangement chunks.

### q080

- question: What evidence shows CrossFirst's growth involved both long-term branch expansion and the 2022 Central acquisition?
- answer: CrossFirst opened its first branch in 2007 and grew through branches and acquisitions; in 2022 it completed the Farmers & Stockmens Bank ('Central') acquisition, adding $389 million of loans and $570 million of deposits.
- source_doc: e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf
- difficulty: hard
- requires_rewrite: True
- requires_multi_hop: True
- evidence excerpt:
  - e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf p.11 chunk `0ec28091604e2b17833ea578499e803675ffefc5`: Since opening our first branch in 2007, we have grown organically primarily by establishing new branches, attracting new clients and expanding our relationships with existing clients, as well as through three strategic acquisitions. Since inception, our strategy has been to be a trusted partner providing customized financial solutions for our clients, which we believe has driven value for our stockholders. We are committed to a culture of serving our clients and communities in extraordinary ways by providing personalized, relationship-based banking. We believe that success is achieved through
  - e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf p.39 chunk `cb23672a0dcbe6fdbf022baf5e73e2ef5bee67de`: 2022 Highlights: Completed the acquisition of Farmers & Stockmens Bank ('Central') adding liquidity, new production talent, and expanding into attractive and growing markets o Added $389 million of loans and $570 million of deposits Total assets were $6.6 billion primarily made up of $5.4 billion in loans and $687 million in securities Loans grew $1.1 billion for the year or 26%; excluding the Central acquisition, loans grew 17% for the year Deposits grew $968 million for the year or 21%; excluding the Central acquisition, deposits grew 9% for the year
- notes: Combines historical branch growth with 2022 acquisition evidence.

## boolean

### q031

- question: Does Holley say it plans to pay cash dividends for the foreseeable future?
- answer: false
- source_doc: 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf p.28 chunk `82f11a7c860717fcd561205ca3b8db5f29c6d4aa`: We do not intend to pay cash dividends for the foreseeable future.
- notes: Evidence directly states Holley does not intend to pay cash dividends for the foreseeable future.

### q032

- question: Did Yellow Pages distribute $100.0 million to shareholders through a share repurchase in 2022?
- answer: true
- source_doc: 9d7a72445aba6860402c3acce75af02dc045f74d.pdf
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - 9d7a72445aba6860402c3acce75af02dc045f74d.pdf p.3 chunk `3b203ae1c1828ca96830a6bad6f1f2217a421df1`: Cash to Shareholders and to Pension Plan. Pursuant to a statutory plan of arrangement, during 2022, we distributed $100.0 million to shareholders by way of a share repurchase from all shareholders on a pro rata basis and advanced $24.0 million of voluntary contributions to our Defined Benefit Pension Plan's wind-up deficit, in addition to our $4.0 million voluntary incremental payments as announced in May 2021 toward our Defined Benefit Pension Plan's wind-up deficit.
- notes: Direct yes/no question supported by Yellow Pages' statutory plan of arrangement language.

### q033

- question: Did Mercia say it became a carbon-neutral company?
- answer: true
- source_doc: ac9aa244462c80705c3ff046542c02c459989742.pdf
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - ac9aa244462c80705c3ff046542c02c459989742.pdf p.5 chunk `60c160920af9ec76e2cd63915a26b3ce2e89818a`: There is always more that can be done, but it was encouraging to see that at our recent senior leadership strategy day, half of the 14 attendees were women. Equally encouraging is that despite it not yet being mandatory for Mercia, we have taken the proactive decision to measure and report on our carbon footprint - for the first time Mercia has been measured and offset its carbon footprint to become a carbon-neutral company. As part of our mantra of 'responsible investing with purpose', we believe in practising what we ask of our investee companies, in terms of both good governance and being
- notes: Boolean Mercia ESG item with explicit carbon-neutral wording.

### q034

- question: Was Mercia's recommended full-year dividend 0.8 pence per share?
- answer: true
- source_doc: ac9aa244462c80705c3ff046542c02c459989742.pdf
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - ac9aa244462c80705c3ff046542c02c459989742.pdf p.5 chunk `171352bdbd9e43652876336072be80146927657a`: In conjunction with the announcement of its interim results in December 2020, Mercia declared its maiden interim dividend of 0.1 pence per share, as the beginning of a progressive dividend policy. In October 2021, this was followed by a maiden final dividend of 0.3 pence per share and an interim dividend last December of 0.3 pence per share. If approved by shareholders at this Septemberʼs Annual General Meeting ('AGM'), the Board is recommending a final dividend of 0.5 pence per share, making 0.8 pence per share for the full year (2021: 0.4 pence per share). If approved, the dividend will be
- notes: Boolean numerical check on Mercia dividend language.

### q035

- question: Did CrossFirst report non-performing loans of $12 million as of December 31, 2022?
- answer: true
- source_doc: e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf p.25 chunk `dc55d63dd76c9107a26bd224cdf03aad98516381`: As of December 31, 2022, our non-performing loans (which consist of non-accrual loans, loans past due 90 days or more and still accruing interest and loans modified under troubled debt restructurings that are not performing in accordance with their modified terms) totaled $12 million and our non-performing assets (which include non-performing loans plus other real estate owned) totaled $13 million. However, we can give no assurance that our non-performing assets will continue to remain at these levels and we may experience increases in non-performing assets in the future. Non-performing
- notes: Boolean numeric fact from CrossFirst risk discussion.

### q036

- question: Did Tradition propose an exceptional distribution of one treasury share for every 100 shares held?
- answer: true
- source_doc: 2779336b845a41544348abb7b3e6e5bd2ff893a2.pdf
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - 2779336b845a41544348abb7b3e6e5bd2ff893a2.pdf p.4 chunk `3c186922691786e5c549fc0324fa4be614b0bf2a`: At the Annual General Meeting to be held on 25 May 2023, the Board will be seeking shareholder approval to pay a cash dividend of CHF 5.50 per share. In addition, an exceptional distribution of treasury shares will also be proposed, with one share to be distributed for every 100 shares held. I would like to thank all the Group's employees for their hard work and commitment throughout the year, and our shareholders for their continued loyalty and trust. Patrick Combes Key Figures
- notes: Boolean shareholder distribution item.

### q037

- question: Were Holley's common stock and warrants listed on the New York Stock Exchange?
- answer: true
- source_doc: 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf p.1 chunk `7320bd02fa692b3aab366e4ea803023f186d4948`: 87-1727560 (I.R.S. Employer Identification No.) 1801 Russellville Road, Bowling Green, KY 42101 (Address of principal executive offices) (270) 782-2900 (Registrant ' s telephone number, including area code) (Former name, former address and former fiscal year, if changed since last report) N/A Securities registered pursuant to Section 12(b) of the Act: Trading symbol(s) Name of each exchange on which registered Title of each class Common Stock, par value $0.0001 Warrants to Purchase Common Stock HLLY New York Stock Exchange New York Stock Exchange HLLY WS
- notes: Boolean securities-listing item based on cover-page table.

### q038

- question: Did Yellow Pages' common share purchase warrants expire on December 20, 2022?
- answer: true
- source_doc: 9d7a72445aba6860402c3acce75af02dc045f74d.pdf
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - 9d7a72445aba6860402c3acce75af02dc045f74d.pdf p.19 chunk `464fe930f57e2cbc93a0f329cd1cbaecdd05a74a`: Share Data Outstanding Share Data 1 On October 4, 2022, the Company repurchased from shareholders pro rata an aggregate of 7,949,125 common shares pursuant to the plan of arrangement (refer to the section ''Plan of Arrangement'' for details. 2 The Common share purchase warrants expired on December 20, 2022.
- notes: Boolean expiration-date item.

### q039

- question: Were Holley's employees represented by a labor union?
- answer: false
- source_doc: 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf p.10 chunk `fb42cd495a75c77b545ddc1ff269c17bba0fe5aa`: distribution center and manufacturing plants. None of our employees are subject to collective bargaining agreements or represented by a labor union. We believe our facilities are in labor markets with ready access to adequate numbers of skilled and unskilled workers, and we believe our relations with our employees are good.
- notes: Evidence says employees were not subject to collective bargaining agreements or represented by a labor union.

### q040

- question: Did Mercia say it invests exclusively in the UK?
- answer: true
- source_doc: ac9aa244462c80705c3ff046542c02c459989742.pdf
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - ac9aa244462c80705c3ff046542c02c459989742.pdf p.14 chunk `4b0c168aab6493db6e430a3e4c4433356a76ef65`: £119.6m Value of direct investment portfolio See more on page 26. investees We invest exclusively in the UK Our teams are conveniently based in the following eight regional locations across the UK. Bristol Manchester Preston Leeds Newcastle Sheffield London Henley-in-Arden
- notes: Boolean Mercia investment-focus item.

### q081

- question: Had Holley ever declared or paid cash dividends on its capital stock?
- answer: false
- source_doc: 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf
- difficulty: medium
- requires_rewrite: True
- requires_multi_hop: False
- evidence excerpt:
  - 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf p.32 chunk `84b37a08caccfb92724217910fa1e6689d10b08e`: Dividend Policy We have never declared or paid any cash dividends on our capital stock, and we do not currently anticipate paying any cash dividends in the foreseeable future. We may consider declaring and paying a cash dividend in the future; however, there can be no assurance that we will do so. Issuer Repurchase of Equity Securities None Unregistered Sales of Equity Securities Except as previously disclosed in a Current Report on Form 8-K, no unregistered sales of the Company's equity securities were made during the year ended December 31, 2022. Stock Performance Graph
- notes: Negation wording: evidence says Holley had never declared or paid cash dividends.

### q082

- question: Did Holley's top seven brands generate 68% of its sales in 2022?
- answer: true
- source_doc: 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf p.7 chunk `511a4a9c6a50d200b21c84f7d683ae7f91993183`: Brands We have a strong portfolio of brands covering various product categories. Our portfolio consists of over 70 brands spanning across 30 product categories. Our top seven brands generated 68% of our sales in 2022. Holley EFI : Currently our largest brand and represented 14% of our sales for 2022. Our Holley EFI brand focuses on electronic fuel injection technology and showcases our new product development engine.
- notes: Boolean numeric check from Holley's brand portfolio chunk.

### q083

- question: Did Yellow Pages' adjusted EBITDA margin decrease to 35.5% in 2022?
- answer: false
- source_doc: 9d7a72445aba6860402c3acce75af02dc045f74d.pdf
- difficulty: hard
- requires_rewrite: True
- requires_multi_hop: False
- evidence excerpt:
  - 9d7a72445aba6860402c3acce75af02dc045f74d.pdf p.11 chunk `7cffeaffd566e371a924e9da8c93a671ad02a2ed`: For the year ended December 31, 2022 Adjusted EBITDA decreased by $5.4 million or 5.3% to $96.6 million, compared to $102.0 million for the same period last year. The adjusted EBITDA margin increased during the year ended December 31, 2022 to 36.0%, compared to 35.5% for the same period last year. The decrease in Adjusted EBITDA for the year ended December 31, 2022, is the result of revenue pressures as well as ongoing investments in our tele-sales force capacity, partially offset by price increases, the efficiencies from optimization in cost of sales, reductions in other operating costs
- notes: Subtle wrong-year/wrong-direction trap: margin increased to 36.0%, compared to 35.5% last year.

### q084

- question: Was Mercia's direct investment portfolio valued at £96.2 million as at 31 March 2022?
- answer: false
- source_doc: ac9aa244462c80705c3ff046542c02c459989742.pdf
- difficulty: hard
- requires_rewrite: True
- requires_multi_hop: False
- evidence excerpt:
  - ac9aa244462c80705c3ff046542c02c459989742.pdf p.18 chunk `ff91bd2abbe86fb4a63313797b8e897ad8445bf0`: As at 31 March 2022, the value of the Group's direct investment portfolio was £119.6million (2021: £96.2million). This reflects an upward fair value movement of £11.4million (2021: £10.1million) and net cash invested of £18.4million (2021: £15.4million), less the realisation of Faradion, which accounted for £5.7million of the total opening portfolio fair value.
- notes: Wrong-year comparator trap: £96.2m was the 2021 comparator, while 2022 was £119.6m.

### q085

- question: Did CrossFirst say its non-performing assets ratio declined to 0.20% by the end of 2022?
- answer: true
- source_doc: e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf
- difficulty: medium
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf p.3 chunk `da118e59c27fe9af087228b1d79469605862e13d`: We have grown our balance sheet by $1.7 billion or over 33% Demand deposits have grown from 13% to 25% of total deposits Net Interest Margin - Fully Tax Equivalent ('FTE') (1) has improved from 3.32% for 2019 to 3.50% for 2022 Credit quality has substantially improved with our non-performing assets ratio declining from 0.97% as of the end of 2019 to only 0.20% as of the end of 2022 Operating revenue has grown to $211 million in 2022 . That is an increase of $61 million or more than 40% from our total operating revenue in 2019
- notes: Boolean credit-quality metric check.

### q086

- question: Were Tradition's net exceptional costs lower in 2022 than in the previous year?
- answer: false
- source_doc: 2779336b845a41544348abb7b3e6e5bd2ff893a2.pdf
- difficulty: hard
- requires_rewrite: True
- requires_multi_hop: False
- evidence excerpt:
  - 2779336b845a41544348abb7b3e6e5bd2ff893a2.pdf p.42 chunk `0646187cdaf2c4f5b72ce4e60ca88b2b22cbc9fe`: Adjusted operating profit before exceptional items was CHF 130.3m against CHF 99.9m in 2021, an increase of 34.0% at constant exchange rates, with an operating margin of 12.7% and 10.5% respectively. Net exceptional costs represented CHF 12.9m compared with CHF 5.8m in the previous year and include a net amount of CHF 7.9m in relation to the Russian invasion of Ukraine. The Group is active in all the major financial markets and operates in numerous currencies. Its results are therefore affected by movements in the exchange rates used to translate local figures into Swiss francs.
- notes: Negation/wrong-direction trap: evidence says CHF 12.9m compared with CHF 5.8m in the previous year.

### q087

- question: Did Yellow Pages' common share purchase warrants expire on December 20, 2022?
- answer: true
- source_doc: 9d7a72445aba6860402c3acce75af02dc045f74d.pdf
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - 9d7a72445aba6860402c3acce75af02dc045f74d.pdf p.19 chunk `464fe930f57e2cbc93a0f329cd1cbaecdd05a74a`: Share Data Outstanding Share Data 1 On October 4, 2022, the Company repurchased from shareholders pro rata an aggregate of 7,949,125 common shares pursuant to the plan of arrangement (refer to the section ''Plan of Arrangement'' for details. 2 The Common share purchase warrants expired on December 20, 2022.
- notes: Direct boolean date check.

### q088

- question: Did Mercia report a 4.4x return for its Faradion direct holding?
- answer: true
- source_doc: ac9aa244462c80705c3ff046542c02c459989742.pdf
- difficulty: medium
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - ac9aa244462c80705c3ff046542c02c459989742.pdf p.18 chunk `9eb8d2808502531479f262a468b101e6dcfc400f`: Faradion was sold in January 2022 to India's Reliance New Energy Solar Ltd, a wholly owned subsidiary of India-based Reliance Industries Ltd, for £100.0million. Total cash proceeds back to Mercia's balance sheet of £19.4million resulted in a realised gain of £9.9million, generating a 4.4x return on Mercia's direct investment cost of £4.4million and a c.72% internal rate of return ('IRR') since the first direct investment in 2017.
- notes: Boolean return-multiple check.

### q089

- question: Were approximately 48% of Holley's full-time employees based primarily around Bowling Green, KY?
- answer: true
- source_doc: 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - 194000c9109c6fa628f1fed33b44ae4c2b8365f4.pdf p.10 chunk `248f9d61c2bbd7d00804948fd9cb0f6752cbcba8`: Holley's employees are integral to our strategic growth and success. We consider our team members to be our most valuable asset and seek to attract and maintain the highest quality talent by offering competitive benefits and wellness services, opportunities to grow professionally, and regular evaluations, among other initiatives. As of December 31, 2022, we employed 1,622 full-time employees and 100 temporary employees. Approximately 48% of our full-time employees are based primarily in our Bowling Green, KY headquarters, distribution center and manufacturing plants. None of our employees are
- notes: Boolean percentage/location check.

### q090

- question: Did CrossFirst say demand deposits shrank from 25% to 13% of total deposits?
- answer: false
- source_doc: e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf
- difficulty: hard
- requires_rewrite: True
- requires_multi_hop: False
- evidence excerpt:
  - e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf p.3 chunk `9d6a0096586367fb79def8184c5bb904b5f0138d`: In terms of 2022 financial performance, we reported $68.6 million in adjusted net income (1) for the year, or adjusted diluted earnings per share of $1.37 (1) . We also grew loans by 26% for the year, with 17% of that growth being organic, and demand deposits grew from 13% to 25% of total deposits. When we look back to our initial public offering in August 2019, and all that has happened at the Bank and to our industry and country since, I am incredibly proud of the progress we have made. We have worked hard to deploy the capital we raised during the IPO through organic balance sheet growth,
- notes: Wrong-direction trap: evidence says demand deposits grew from 13% to 25%.

## ood

### q041

- question: What was Apple's research and development expense in fiscal 2022?
- answer: Not sure based on the provided documents.
- source_doc: N/A - not supported by current 5 PDF set
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - None; this is an OOD item.
- notes: OOD because the current PDF set contains Holley, Tradition, Yellow Pages, Mercia, and CrossFirst reports, not Apple financial statements.

### q042

- question: What greenhouse gas emissions reduction target did Tesla set for 2030 in these documents?
- answer: Not sure based on the provided documents.
- source_doc: N/A - not supported by current 5 PDF set
- difficulty: medium
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - None; this is an OOD item.
- notes: OOD because none of the current five PDFs is a Tesla report or provides sufficient evidence for Tesla's 2030 emissions targets.

### q043

- question: What was NVIDIA's data center revenue in fiscal 2024?
- answer: Not sure based on the provided documents.
- source_doc: N/A - not supported by current 5 PDF set
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - None; this is an OOD item.
- notes: OOD because the current PDF set covers Holley, Tradition, Yellow Pages, Mercia, and CrossFirst, not NVIDIA.

### q044

- question: How much revenue did Microsoft Azure generate in fiscal 2023?
- answer: Not sure based on the provided documents.
- source_doc: N/A - not supported by current 5 PDF set
- difficulty: medium
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - None; this is an OOD item.
- notes: OOD because the current documents do not include Microsoft segment reporting.

### q045

- question: What capital expenditures did Amazon report for AWS infrastructure in 2022?
- answer: Not sure based on the provided documents.
- source_doc: N/A - not supported by current 5 PDF set
- difficulty: medium
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - None; this is an OOD item.
- notes: OOD because Amazon/AWS financial disclosures are not part of the current five-PDF corpus.

### q046

- question: How many paid subscribers did Netflix report at the end of 2022?
- answer: Not sure based on the provided documents.
- source_doc: N/A - not supported by current 5 PDF set
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - None; this is an OOD item.
- notes: OOD because no Netflix annual report or subscriber disclosure is included in the current corpus.

### q047

- question: What was Meta's Facebook daily active users figure for December 2022?
- answer: Not sure based on the provided documents.
- source_doc: N/A - not supported by current 5 PDF set
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - None; this is an OOD item.
- notes: OOD because Meta platform metrics are not covered by the current PDF set.

### q048

- question: What was Coca-Cola's net operating revenue in 2022?
- answer: Not sure based on the provided documents.
- source_doc: N/A - not supported by current 5 PDF set
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - None; this is an OOD item.
- notes: OOD because the current five PDFs do not include Coca-Cola filings.

### q049

- question: How many commercial airplanes did Boeing deliver in 2022?
- answer: Not sure based on the provided documents.
- source_doc: N/A - not supported by current 5 PDF set
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - None; this is an OOD item.
- notes: OOD because Boeing delivery data is outside the current five-PDF corpus.

### q050

- question: What was Pfizer's Comirnaty revenue in 2022?
- answer: Not sure based on the provided documents.
- source_doc: N/A - not supported by current 5 PDF set
- difficulty: medium
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - None; this is an OOD item.
- notes: OOD because Pfizer product revenue disclosures are not included in the current documents.

### q091

- question: What was Alphabet's Google Cloud operating income in 2022?
- answer: Not sure based on the provided documents.
- source_doc: N/A - not supported by current 5 PDF set
- difficulty: medium
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - None; this is an OOD item.
- notes: OOD because Alphabet/Google Cloud segment results are not in the current five-PDF corpus.

### q092

- question: How many vehicles did Ford sell in Europe in 2022?
- answer: Not sure based on the provided documents.
- source_doc: N/A - not supported by current 5 PDF set
- difficulty: medium
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - None; this is an OOD item.
- notes: OOD because no Ford annual report or vehicle-delivery disclosure is included.

### q093

- question: What was Starbucks' comparable store sales growth in China in fiscal 2022?
- answer: Not sure based on the provided documents.
- source_doc: N/A - not supported by current 5 PDF set
- difficulty: medium
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - None; this is an OOD item.
- notes: OOD because Starbucks operating metrics are outside the current document set.

### q094

- question: What was JPMorgan Chase's CET1 capital ratio at year-end 2022?
- answer: Not sure based on the provided documents.
- source_doc: N/A - not supported by current 5 PDF set
- difficulty: medium
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - None; this is an OOD item.
- notes: Plausible finance question but unsupported because JPMorgan filings are not in this corpus.

### q095

- question: How much did Shell spend on renewable energy investments in 2022?
- answer: Not sure based on the provided documents.
- source_doc: N/A - not supported by current 5 PDF set
- difficulty: medium
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - None; this is an OOD item.
- notes: OOD because Shell energy-transition disclosures are not included in the current PDFs.

### q096

- question: What was Disney's direct-to-consumer operating loss in fiscal 2022?
- answer: Not sure based on the provided documents.
- source_doc: N/A - not supported by current 5 PDF set
- difficulty: medium
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - None; this is an OOD item.
- notes: OOD because Disney segment reporting is not part of the current corpus.

### q097

- question: What was Toyota's global hybrid vehicle sales volume in fiscal 2022?
- answer: Not sure based on the provided documents.
- source_doc: N/A - not supported by current 5 PDF set
- difficulty: medium
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - None; this is an OOD item.
- notes: OOD because Toyota sales-volume data is absent from the current five PDFs.

### q098

- question: What was Visa's payments volume growth in 2022?
- answer: Not sure based on the provided documents.
- source_doc: N/A - not supported by current 5 PDF set
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - None; this is an OOD item.
- notes: OOD because Visa payment-network metrics are not included in the corpus.

### q099

- question: How many active riders did Uber report in 2022?
- answer: Not sure based on the provided documents.
- source_doc: N/A - not supported by current 5 PDF set
- difficulty: easy
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - None; this is an OOD item.
- notes: OOD because Uber user metrics are unsupported by these documents.

### q100

- question: What was Unilever's underlying sales growth in emerging markets in 2022?
- answer: Not sure based on the provided documents.
- source_doc: N/A - not supported by current 5 PDF set
- difficulty: medium
- requires_rewrite: False
- requires_multi_hop: False
- evidence excerpt:
  - None; this is an OOD item.
- notes: OOD because Unilever geographic sales metrics are outside the current five-PDF set.
