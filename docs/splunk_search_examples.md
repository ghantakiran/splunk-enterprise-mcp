# Splunk Search & Dashboard Examples for MCP Events

## List All Model Events
```spl
index="main" sourcetype="mcp:model_event"
| table _time event.event_type event.model_context.name event.model_context.version event.details
```

## Model Lifecycle Timeline
```spl
index="main" sourcetype="mcp:model_event"
| stats list(event.event_type) as events by event.model_context.model_id, event.model_context.name, event.model_context.version
```

## Dashboard Panel (XML)
```xml
<panel>
  <title>Model Events Over Time</title>
  <chart>
    <search>
      <query>index="main" sourcetype="mcp:model_event" | timechart count by event.event_type</query>
    </search>
    <option name="charting.chart">line</option>
  </chart>
</panel>
``` 