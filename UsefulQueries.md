# Useful Queries

## Get all assessment responses and questions for a specific user:
```sql
select
	ar.id, aq.question_id, aq.order_id, aq.question, aq.options ,arq.response_value 
from
	assessment_response ar 
	left outer join assessment_response_question arq on arq.assessment_response_id = ar.id 
	left outer join assessment_question aq on aq.id = arq.assessment_question_id
	left outer join "user" u on u.id = ar.user_id 
where
	u.first_name='Sarah' and u.last_name='Chen'
order by 	
	aq.order_id asc	
```

## Get the latest generated recommendation for a specific user:
```sql
select 
	 pga.id as "generate_id", pgca.system_prompt , pgca.message_prompt, pgca.response 
from 
	program_generate_audit pga 
	left outer join program_generate_llm_audit pgca on pga.id = pgca.program_generate_audit_id 
	left outer join assessment_response ar on pga.assessment_response_id = ar.id 
	left outer join "user" u on u.id = ar.user_id
where
	u.first_name='Sarah' and u.last_name='Chen' 
order by 
	pga.created_at desc 
limit 1;
```



