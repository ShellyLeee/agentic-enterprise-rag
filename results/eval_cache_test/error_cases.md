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
