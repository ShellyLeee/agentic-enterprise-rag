# Error Cases

Grouped smoke-test diagnostics. These are lexical/proxy checks, not human judgments.

## naive

### False refusals on answerable questions

- None.

### False answers on OOD questions

- `q017` (ood)
  - question: What is the company's policy on pet insurance?
  - gold: I don't know based on the provided context.
  - predicted: source: sample_policy.md page: 1 section: Expense Reimbursement score: 0.179787 text: Air travel should be booked in economy class unless a written exception is approved by an executive. [chunk:1:5d842118]
  - decision: answer
  - f1: 0.000
  - retrieval_hit: 0.0
  - unsupported_proxy: 1.0

- `q018` (ood)
  - question: What is the parental leave policy?
  - gold: I don't know based on the provided context.
  - predicted: source: sample_policy.md page: 1 section: Vacation Policy score: 0.150063 text: Vacation requests should be submitted to the employee's manager at least two weeks before the planned absence. [chunk:1:58f0057b]
  - decision: answer
  - f1: 0.047
  - retrieval_hit: 0.0
  - unsupported_proxy: 1.0

- `q019` (ood)
  - question: How much does the company contribute to employee 401k accounts?
  - gold: I don't know based on the provided context.
  - predicted: ## Security and Data Handling Employees must protect company, customer, and employee data according to its classification. [chunk:1:5d842118]
  - decision: answer
  - f1: 0.000
  - retrieval_hit: 0.0
  - unsupported_proxy: 1.0

- `q020` (ood)
  - question: Does the policy cover tuition reimbursement for graduate school?
  - gold: I don't know based on the provided context.
  - predicted: source: sample_policy.md page: 1 section: Expense Reimbursement score: 0.12666 text: Air travel should be booked in economy class unless a written exception is approved by an executive. [chunk:2:5d842118]
  - decision: answer
  - f1: 0.000
  - retrieval_hit: 0.0
  - unsupported_proxy: 1.0

### Low-F1 answered cases

- `q008` (simple)
  - question: What travel class should air travel normally be booked in?
  - gold: Economy class
  - predicted: source: sample_policy.md page: 1 section: Expense Reimbursement score: 0.326679 text: Air travel should be booked in economy class unless a written exception is approved by an executive. [chunk:1:5d842118]
  - decision: answer
  - f1: 0.114
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q009` (simple)
  - question: What must employees do if they suspect a security incident?
  - gold: Report it to the security team immediately
  - predicted: Employees must complete annual security training and follow additional handling requirements for regulated, financial, or personally identifiable information. [chunk:1:fcd9abd0]
  - decision: answer
  - f1: 0.071
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q011` (comparison)
  - question: Which allowance is larger: vacation days for new employees or remote work days per week?
  - gold: Vacation days for new employees
  - predicted: ## Remote Work Policy Employees may work remotely up to three days per week when their role, team commitments, and manager approval allow it. [chunk:1:58f0057b]
  - decision: answer
  - f1: 0.129
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q013` (comparison)
  - question: Which requires executive approval: economy air travel or an exception to economy class?
  - gold: An exception to economy class
  - predicted: source: sample_policy.md page: 1 section: Expense Reimbursement score: 0.256843 text: Air travel should be booked in economy class unless a written exception is approved by an executive. [chunk:1:5d842118]
  - decision: answer
  - f1: 0.211
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

### Retrieval misses

- `q017` (ood)
  - question: What is the company's policy on pet insurance?
  - gold: I don't know based on the provided context.
  - predicted: source: sample_policy.md page: 1 section: Expense Reimbursement score: 0.179787 text: Air travel should be booked in economy class unless a written exception is approved by an executive. [chunk:1:5d842118]
  - decision: answer
  - f1: 0.000
  - retrieval_hit: 0.0
  - unsupported_proxy: 1.0

- `q018` (ood)
  - question: What is the parental leave policy?
  - gold: I don't know based on the provided context.
  - predicted: source: sample_policy.md page: 1 section: Vacation Policy score: 0.150063 text: Vacation requests should be submitted to the employee's manager at least two weeks before the planned absence. [chunk:1:58f0057b]
  - decision: answer
  - f1: 0.047
  - retrieval_hit: 0.0
  - unsupported_proxy: 1.0

- `q019` (ood)
  - question: How much does the company contribute to employee 401k accounts?
  - gold: I don't know based on the provided context.
  - predicted: ## Security and Data Handling Employees must protect company, customer, and employee data according to its classification. [chunk:1:5d842118]
  - decision: answer
  - f1: 0.000
  - retrieval_hit: 0.0
  - unsupported_proxy: 1.0

- `q020` (ood)
  - question: Does the policy cover tuition reimbursement for graduate school?
  - gold: I don't know based on the provided context.
  - predicted: source: sample_policy.md page: 1 section: Expense Reimbursement score: 0.12666 text: Air travel should be booked in economy class unless a written exception is approved by an executive. [chunk:2:5d842118]
  - decision: answer
  - f1: 0.000
  - retrieval_hit: 0.0
  - unsupported_proxy: 1.0

### Unsupported answers

- `q017` (ood)
  - question: What is the company's policy on pet insurance?
  - gold: I don't know based on the provided context.
  - predicted: source: sample_policy.md page: 1 section: Expense Reimbursement score: 0.179787 text: Air travel should be booked in economy class unless a written exception is approved by an executive. [chunk:1:5d842118]
  - decision: answer
  - f1: 0.000
  - retrieval_hit: 0.0
  - unsupported_proxy: 1.0

- `q018` (ood)
  - question: What is the parental leave policy?
  - gold: I don't know based on the provided context.
  - predicted: source: sample_policy.md page: 1 section: Vacation Policy score: 0.150063 text: Vacation requests should be submitted to the employee's manager at least two weeks before the planned absence. [chunk:1:58f0057b]
  - decision: answer
  - f1: 0.047
  - retrieval_hit: 0.0
  - unsupported_proxy: 1.0

- `q019` (ood)
  - question: How much does the company contribute to employee 401k accounts?
  - gold: I don't know based on the provided context.
  - predicted: ## Security and Data Handling Employees must protect company, customer, and employee data according to its classification. [chunk:1:5d842118]
  - decision: answer
  - f1: 0.000
  - retrieval_hit: 0.0
  - unsupported_proxy: 1.0

- `q020` (ood)
  - question: Does the policy cover tuition reimbursement for graduate school?
  - gold: I don't know based on the provided context.
  - predicted: source: sample_policy.md page: 1 section: Expense Reimbursement score: 0.12666 text: Air travel should be booked in economy class unless a written exception is approved by an executive. [chunk:2:5d842118]
  - decision: answer
  - f1: 0.000
  - retrieval_hit: 0.0
  - unsupported_proxy: 1.0

## rerank

### False refusals on answerable questions

- None.

### False answers on OOD questions

- `q017` (ood)
  - question: What is the company's policy on pet insurance?
  - gold: I don't know based on the provided context.
  - predicted: source: sample_policy.md page: 1 section: Vacation Policy score: 0.079446 text: # Enterprise Employee Policy Handbook ## Vacation Policy Full-time employees accrue paid vacation time based on tenure and employment status. [chunk:1:60968f54]
  - decision: answer
  - f1: 0.091
  - retrieval_hit: 0.0
  - unsupported_proxy: 1.0

- `q018` (ood)
  - question: What is the parental leave policy?
  - gold: I don't know based on the provided context.
  - predicted: source: sample_policy.md page: 1 section: Vacation Policy score: 0.06958 text: # Enterprise Employee Policy Handbook ## Vacation Policy Full-time employees accrue paid vacation time based on tenure and employment status. [chunk:1:60968f54]
  - decision: answer
  - f1: 0.091
  - retrieval_hit: 0.0
  - unsupported_proxy: 1.0

- `q019` (ood)
  - question: How much does the company contribute to employee 401k accounts?
  - gold: I don't know based on the provided context.
  - predicted: ## Security and Data Handling Employees must protect company, customer, and employee data according to its classification. [chunk:1:5d842118]
  - decision: answer
  - f1: 0.000
  - retrieval_hit: 0.0
  - unsupported_proxy: 1.0

- `q020` (ood)
  - question: Does the policy cover tuition reimbursement for graduate school?
  - gold: I don't know based on the provided context.
  - predicted: source: sample_policy.md page: 1 section: Expense Reimbursement score: 0.12666 text: Air travel should be booked in economy class unless a written exception is approved by an executive. [chunk:5:5d842118]
  - decision: answer
  - f1: 0.000
  - retrieval_hit: 0.0
  - unsupported_proxy: 1.0

### Low-F1 answered cases

- `q008` (simple)
  - question: What travel class should air travel normally be booked in?
  - gold: Economy class
  - predicted: source: sample_policy.md page: 1 section: Expense Reimbursement score: 0.326679 text: Air travel should be booked in economy class unless a written exception is approved by an executive. [chunk:1:5d842118]
  - decision: answer
  - f1: 0.114
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q009` (simple)
  - question: What must employees do if they suspect a security incident?
  - gold: Report it to the security team immediately
  - predicted: Employees must complete annual security training and follow additional handling requirements for regulated, financial, or personally identifiable information. [chunk:1:fcd9abd0]
  - decision: answer
  - f1: 0.071
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q011` (comparison)
  - question: Which allowance is larger: vacation days for new employees or remote work days per week?
  - gold: Vacation days for new employees
  - predicted: ## Remote Work Policy Employees may work remotely up to three days per week when their role, team commitments, and manager approval allow it. [chunk:1:58f0057b]
  - decision: answer
  - f1: 0.129
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q013` (comparison)
  - question: Which requires executive approval: economy air travel or an exception to economy class?
  - gold: An exception to economy class
  - predicted: source: sample_policy.md page: 1 section: Expense Reimbursement score: 0.256843 text: Air travel should be booked in economy class unless a written exception is approved by an executive. [chunk:1:5d842118]
  - decision: answer
  - f1: 0.211
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

### Retrieval misses

- `q017` (ood)
  - question: What is the company's policy on pet insurance?
  - gold: I don't know based on the provided context.
  - predicted: source: sample_policy.md page: 1 section: Vacation Policy score: 0.079446 text: # Enterprise Employee Policy Handbook ## Vacation Policy Full-time employees accrue paid vacation time based on tenure and employment status. [chunk:1:60968f54]
  - decision: answer
  - f1: 0.091
  - retrieval_hit: 0.0
  - unsupported_proxy: 1.0

- `q018` (ood)
  - question: What is the parental leave policy?
  - gold: I don't know based on the provided context.
  - predicted: source: sample_policy.md page: 1 section: Vacation Policy score: 0.06958 text: # Enterprise Employee Policy Handbook ## Vacation Policy Full-time employees accrue paid vacation time based on tenure and employment status. [chunk:1:60968f54]
  - decision: answer
  - f1: 0.091
  - retrieval_hit: 0.0
  - unsupported_proxy: 1.0

- `q019` (ood)
  - question: How much does the company contribute to employee 401k accounts?
  - gold: I don't know based on the provided context.
  - predicted: ## Security and Data Handling Employees must protect company, customer, and employee data according to its classification. [chunk:1:5d842118]
  - decision: answer
  - f1: 0.000
  - retrieval_hit: 0.0
  - unsupported_proxy: 1.0

- `q020` (ood)
  - question: Does the policy cover tuition reimbursement for graduate school?
  - gold: I don't know based on the provided context.
  - predicted: source: sample_policy.md page: 1 section: Expense Reimbursement score: 0.12666 text: Air travel should be booked in economy class unless a written exception is approved by an executive. [chunk:5:5d842118]
  - decision: answer
  - f1: 0.000
  - retrieval_hit: 0.0
  - unsupported_proxy: 1.0

### Unsupported answers

- `q017` (ood)
  - question: What is the company's policy on pet insurance?
  - gold: I don't know based on the provided context.
  - predicted: source: sample_policy.md page: 1 section: Vacation Policy score: 0.079446 text: # Enterprise Employee Policy Handbook ## Vacation Policy Full-time employees accrue paid vacation time based on tenure and employment status. [chunk:1:60968f54]
  - decision: answer
  - f1: 0.091
  - retrieval_hit: 0.0
  - unsupported_proxy: 1.0

- `q018` (ood)
  - question: What is the parental leave policy?
  - gold: I don't know based on the provided context.
  - predicted: source: sample_policy.md page: 1 section: Vacation Policy score: 0.06958 text: # Enterprise Employee Policy Handbook ## Vacation Policy Full-time employees accrue paid vacation time based on tenure and employment status. [chunk:1:60968f54]
  - decision: answer
  - f1: 0.091
  - retrieval_hit: 0.0
  - unsupported_proxy: 1.0

- `q019` (ood)
  - question: How much does the company contribute to employee 401k accounts?
  - gold: I don't know based on the provided context.
  - predicted: ## Security and Data Handling Employees must protect company, customer, and employee data according to its classification. [chunk:1:5d842118]
  - decision: answer
  - f1: 0.000
  - retrieval_hit: 0.0
  - unsupported_proxy: 1.0

- `q020` (ood)
  - question: Does the policy cover tuition reimbursement for graduate school?
  - gold: I don't know based on the provided context.
  - predicted: source: sample_policy.md page: 1 section: Expense Reimbursement score: 0.12666 text: Air travel should be booked in economy class unless a written exception is approved by an executive. [chunk:5:5d842118]
  - decision: answer
  - f1: 0.000
  - retrieval_hit: 0.0
  - unsupported_proxy: 1.0

## agentic_conservative

### False refusals on answerable questions

- `q001` (simple)
  - question: How many vacation days do new employees accrue?
  - gold: 15 vacation days per calendar year
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Evidence remains insufficient after allowed retries. Best available scores: [0.669505, 0.54868, 0.233631].
  - decision: refuse
  - f1: 0.000
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q002` (simple)
  - question: How many vacation days do employees with more than five years of service accrue?
  - gold: 20 vacation days per calendar year
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Evidence remains insufficient after allowed retries. Best available scores: [0.799073, 0.557322, 0.219523].
  - decision: refuse
  - f1: 0.000
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q003` (simple)
  - question: How far in advance should vacation requests be submitted?
  - gold: At least two weeks before the planned absence
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Evidence remains insufficient after allowed retries. Best available scores: [0.474872, 0.382842, 0.129641].
  - decision: refuse
  - f1: 0.051
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q004` (simple)
  - question: How many vacation days may carry over for one calendar year?
  - gold: Up to five days
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Evidence remains insufficient after allowed retries. Best available scores: [0.705409, 0.594949, 0.249404].
  - decision: refuse
  - f1: 0.057
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q005` (simple)
  - question: How many days per week may employees work remotely?
  - gold: Up to three days per week
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Evidence remains insufficient after allowed retries. Best available scores: [0.662195, 0.608199, 0.257485].
  - decision: refuse
  - f1: 0.054
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q006` (simple)
  - question: What are the core collaboration hours for remote employees?
  - gold: 10:00 a.m. to 3:00 p.m.
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Evidence remains insufficient after allowed retries. Best available scores: [0.516557, 0.413299, 0.211289].
  - decision: refuse
  - f1: 0.050
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q007` (simple)
  - question: Within how many days should business expenses be submitted?
  - gold: Within 30 days of purchase
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Evidence remains insufficient after allowed retries. Best available scores: [0.599756, 0.522133, 0.351976].
  - decision: refuse
  - f1: 0.000
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q008` (simple)
  - question: What travel class should air travel normally be booked in?
  - gold: Economy class
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Evidence remains insufficient after allowed retries. Best available scores: [0.398087, 0.372474, 0.179284].
  - decision: refuse
  - f1: 0.000
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q009` (simple)
  - question: What must employees do if they suspect a security incident?
  - gold: Report it to the security team immediately
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Evidence remains insufficient after allowed retries. Best available scores: [0.262445, 0.206197, 0.152783].
  - decision: refuse
  - f1: 0.105
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q010` (simple)
  - question: Where may confidential data be stored?
  - gold: Only in approved systems
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Evidence remains insufficient after allowed retries. Best available scores: [0.214599, 0.192748, 0.130066].
  - decision: refuse
  - f1: 0.000
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q011` (comparison)
  - question: Which allowance is larger: vacation days for new employees or remote work days per week?
  - gold: Vacation days for new employees
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Evidence remains insufficient after allowed retries. Best available scores: [0.628887, 0.610133, 0.245803].
  - decision: refuse
  - f1: 0.000
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q012` (comparison)
  - question: Which deadline is longer: submitting vacation requests in advance or submitting business expenses after purchase?
  - gold: Submitting business expenses after purchase
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Evidence remains insufficient after allowed retries. Best available scores: [0.419435, 0.366775, 0.170941].
  - decision: refuse
  - f1: 0.056
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q013` (comparison)
  - question: Which requires executive approval: economy air travel or an exception to economy class?
  - gold: An exception to economy class
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Evidence remains insufficient after allowed retries. Best available scores: [0.388092, 0.364208, 0.175187].
  - decision: refuse
  - f1: 0.056
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q014` (multi_hop)
  - question: If an employee works remotely and handles regulated customer data, what additional controls may be required?
  - gold: Approved devices, private workspaces, and mandatory VPN connectivity
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Evidence remains insufficient after allowed retries. Best available scores: [0.288278, 0.185312, 0.164771].
  - decision: refuse
  - f1: 0.000
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q015` (multi_hop)
  - question: If an employee buys software for a client meeting, what documentation and deadline apply?
  - gold: Attach itemized receipts and submit within 30 days of purchase
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Evidence remains insufficient after allowed retries. Best available scores: [0.41571, 0.402277, 0.222911].
  - decision: refuse
  - f1: 0.000
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q016` (multi_hop)
  - question: What must employees complete and follow for regulated or personally identifiable information?
  - gold: Annual security training and additional handling requirements
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Evidence remains insufficient after allowed retries. Best available scores: [0.453557, 0.267261, 0.168034].
  - decision: refuse
  - f1: 0.000
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

### False answers on OOD questions

- None.

### Low-F1 answered cases

- None.

### Retrieval misses

- `q017` (ood)
  - question: What is the company's policy on pet insurance?
  - gold: I don't know based on the provided context.
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Query appears out of scope and retrieved evidence is weak. Best available scores: [0.091287, 0.070014, 0.066227].
  - decision: refuse
  - f1: 0.182
  - retrieval_hit: 0.0
  - unsupported_proxy: 0.0

- `q018` (ood)
  - question: What is the parental leave policy?
  - gold: I don't know based on the provided context.
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Query appears out of scope and retrieved evidence is weak. Best available scores: [0.105409, 0.076472, 0.0].
  - decision: refuse
  - f1: 0.182
  - retrieval_hit: 0.0
  - unsupported_proxy: 0.0

- `q019` (ood)
  - question: How much does the company contribute to employee 401k accounts?
  - gold: I don't know based on the provided context.
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Query appears out of scope and retrieved evidence is weak. Best available scores: [0.171499, 0.074536, 0.054074].
  - decision: refuse
  - f1: 0.182
  - retrieval_hit: 0.0
  - unsupported_proxy: 0.0

- `q020` (ood)
  - question: Does the policy cover tuition reimbursement for graduate school?
  - gold: I don't know based on the provided context.
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Query appears out of scope and retrieved evidence is weak. Best available scores: [0.101015, 0.100125, 0.071429].
  - decision: refuse
  - f1: 0.182
  - retrieval_hit: 0.0
  - unsupported_proxy: 0.0

### Unsupported answers

- None.

## agentic_balanced

### False refusals on answerable questions

- `q003` (simple)
  - question: How far in advance should vacation requests be submitted?
  - gold: At least two weeks before the planned absence
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Evidence remains insufficient after allowed retries. Best available scores: [0.474872, 0.382842, 0.129641].
  - decision: refuse
  - f1: 0.051
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q008` (simple)
  - question: What travel class should air travel normally be booked in?
  - gold: Economy class
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Evidence remains insufficient after allowed retries. Best available scores: [0.398087, 0.372474, 0.179284].
  - decision: refuse
  - f1: 0.000
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q009` (simple)
  - question: What must employees do if they suspect a security incident?
  - gold: Report it to the security team immediately
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Evidence remains insufficient after allowed retries. Best available scores: [0.262445, 0.206197, 0.152783].
  - decision: refuse
  - f1: 0.105
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q010` (simple)
  - question: Where may confidential data be stored?
  - gold: Only in approved systems
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Evidence remains insufficient after allowed retries. Best available scores: [0.214599, 0.192748, 0.130066].
  - decision: refuse
  - f1: 0.000
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q012` (comparison)
  - question: Which deadline is longer: submitting vacation requests in advance or submitting business expenses after purchase?
  - gold: Submitting business expenses after purchase
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Evidence remains insufficient after allowed retries. Best available scores: [0.419435, 0.366775, 0.170941].
  - decision: refuse
  - f1: 0.056
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q013` (comparison)
  - question: Which requires executive approval: economy air travel or an exception to economy class?
  - gold: An exception to economy class
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Evidence remains insufficient after allowed retries. Best available scores: [0.388092, 0.364208, 0.175187].
  - decision: refuse
  - f1: 0.056
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q014` (multi_hop)
  - question: If an employee works remotely and handles regulated customer data, what additional controls may be required?
  - gold: Approved devices, private workspaces, and mandatory VPN connectivity
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Evidence remains insufficient after allowed retries. Best available scores: [0.288278, 0.185312, 0.164771].
  - decision: refuse
  - f1: 0.000
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q016` (multi_hop)
  - question: What must employees complete and follow for regulated or personally identifiable information?
  - gold: Annual security training and additional handling requirements
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Evidence remains insufficient after allowed retries. Best available scores: [0.453557, 0.267261, 0.168034].
  - decision: refuse
  - f1: 0.000
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

### False answers on OOD questions

- None.

### Low-F1 answered cases

- `q011` (comparison)
  - question: Which allowance is larger: vacation days for new employees or remote work days per week?
  - gold: Vacation days for new employees
  - predicted: ## Remote Work Policy Employees may work remotely up to three days per week when their role, team commitments, and manager approval allow it. [chunk:1:58f0057b]
  - decision: answer
  - f1: 0.129
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

### Retrieval misses

- `q017` (ood)
  - question: What is the company's policy on pet insurance?
  - gold: I don't know based on the provided context.
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Query appears out of scope and retrieved evidence is weak. Best available scores: [0.091287, 0.070014, 0.066227].
  - decision: refuse
  - f1: 0.182
  - retrieval_hit: 0.0
  - unsupported_proxy: 0.0

- `q018` (ood)
  - question: What is the parental leave policy?
  - gold: I don't know based on the provided context.
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Query appears out of scope and retrieved evidence is weak. Best available scores: [0.105409, 0.076472, 0.0].
  - decision: refuse
  - f1: 0.182
  - retrieval_hit: 0.0
  - unsupported_proxy: 0.0

- `q019` (ood)
  - question: How much does the company contribute to employee 401k accounts?
  - gold: I don't know based on the provided context.
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Query appears out of scope and retrieved evidence is weak. Best available scores: [0.171499, 0.074536, 0.054074].
  - decision: refuse
  - f1: 0.182
  - retrieval_hit: 0.0
  - unsupported_proxy: 0.0

- `q020` (ood)
  - question: Does the policy cover tuition reimbursement for graduate school?
  - gold: I don't know based on the provided context.
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Query appears out of scope and retrieved evidence is weak. Best available scores: [0.101015, 0.100125, 0.071429].
  - decision: refuse
  - f1: 0.182
  - retrieval_hit: 0.0
  - unsupported_proxy: 0.0

### Unsupported answers

- None.

## agentic_aggressive

### False refusals on answerable questions

- None.

### False answers on OOD questions

- `q019` (ood)
  - question: How much does the company contribute to employee 401k accounts?
  - gold: I don't know based on the provided context.
  - predicted: ## Security and Data Handling Employees must protect company, customer, and employee data according to its classification. [chunk:3:5d842118]
  - decision: answer
  - f1: 0.000
  - retrieval_hit: 0.0
  - unsupported_proxy: 1.0

### Low-F1 answered cases

- `q008` (simple)
  - question: What travel class should air travel normally be booked in?
  - gold: Economy class
  - predicted: source: sample_policy.md page: 1 section: Expense Reimbursement score: 0.326679 text: Air travel should be booked in economy class unless a written exception is approved by an executive. [chunk:1:5d842118]
  - decision: answer
  - f1: 0.114
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q009` (simple)
  - question: What must employees do if they suspect a security incident?
  - gold: Report it to the security team immediately
  - predicted: Employees must complete annual security training and follow additional handling requirements for regulated, financial, or personally identifiable information. [chunk:1:fcd9abd0]
  - decision: answer
  - f1: 0.071
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q011` (comparison)
  - question: Which allowance is larger: vacation days for new employees or remote work days per week?
  - gold: Vacation days for new employees
  - predicted: ## Remote Work Policy Employees may work remotely up to three days per week when their role, team commitments, and manager approval allow it. [chunk:1:58f0057b]
  - decision: answer
  - f1: 0.129
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

- `q013` (comparison)
  - question: Which requires executive approval: economy air travel or an exception to economy class?
  - gold: An exception to economy class
  - predicted: source: sample_policy.md page: 1 section: Expense Reimbursement score: 0.244998 text: Air travel should be booked in economy class unless a written exception is approved by an executive. [chunk:3:5d842118]
  - decision: answer
  - f1: 0.211
  - retrieval_hit: 1.0
  - unsupported_proxy: 0.0

### Retrieval misses

- `q017` (ood)
  - question: What is the company's policy on pet insurance?
  - gold: I don't know based on the provided context.
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Query appears out of scope and retrieved evidence is weak. Best available scores: [0.091287, 0.070014, 0.066227].
  - decision: refuse
  - f1: 0.182
  - retrieval_hit: 0.0
  - unsupported_proxy: 0.0

- `q018` (ood)
  - question: What is the parental leave policy?
  - gold: I don't know based on the provided context.
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Query appears out of scope and retrieved evidence is weak. Best available scores: [0.105409, 0.076472, 0.0].
  - decision: refuse
  - f1: 0.182
  - retrieval_hit: 0.0
  - unsupported_proxy: 0.0

- `q019` (ood)
  - question: How much does the company contribute to employee 401k accounts?
  - gold: I don't know based on the provided context.
  - predicted: ## Security and Data Handling Employees must protect company, customer, and employee data according to its classification. [chunk:3:5d842118]
  - decision: answer
  - f1: 0.000
  - retrieval_hit: 0.0
  - unsupported_proxy: 1.0

- `q020` (ood)
  - question: Does the policy cover tuition reimbursement for graduate school?
  - gold: I don't know based on the provided context.
  - predicted: I don't have enough grounded evidence to answer this question from the available documents. Reason: Query appears out of scope and retrieved evidence is weak. Best available scores: [0.101015, 0.100125, 0.071429].
  - decision: refuse
  - f1: 0.182
  - retrieval_hit: 0.0
  - unsupported_proxy: 0.0

### Unsupported answers

- `q019` (ood)
  - question: How much does the company contribute to employee 401k accounts?
  - gold: I don't know based on the provided context.
  - predicted: ## Security and Data Handling Employees must protect company, customer, and employee data according to its classification. [chunk:3:5d842118]
  - decision: answer
  - f1: 0.000
  - retrieval_hit: 0.0
  - unsupported_proxy: 1.0
