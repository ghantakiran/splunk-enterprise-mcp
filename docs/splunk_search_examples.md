# Splunk Search & Dashboard Examples for MCP Events

## List All Model Events
```spl
index="main" sourcetype=mcp:model_event
| table _time event.event_type event.model_context.name event.model_context.version event.details
```

## Model Lifecycle Timeline
```spl
index="main" sourcetype=mcp:model_event
| stats list(event.event_type) as events by event.model_context.model_id, event.model_context.name, event.model_context.version
```

## Traceability: User Activity Log
```spl
index="main" sourcetype=mcp:traceability action="search" OR action="view_dashboard"
| table timestamp user session_id action resource status
```

## Traceability: Admin Audit Trail
```spl
index="main" sourcetype=mcp:traceability action="add_user" OR action="remove_user" OR action="update_user_role"
| table timestamp user session_id action resource status target_user target_role
```

## Traceability: Security/Compliance Monitoring
```spl
index="main" sourcetype=mcp:traceability action="investigate_security_event"
| table timestamp user session_id action event_id status
```

## Dashboard Panel (XML)
```xml
<panel>
  <title>Traceability: User & Admin Actions Over Time</title>
  <chart>
    <search>
      <query>index="main" sourcetype=mcp:traceability | timechart count by action</query>
    </search>
    <option name="charting.chart">line</option>
  </chart>
</panel>
``` 