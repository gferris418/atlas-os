# ChatGPT adapter

## Discovery order

`atlas-os.yaml -> core specifications -> applicable registries -> this contract -> active controls -> task execution`

## Contract

- **Capabilities:** conversation, tool use when exposed, connected private sources when authorized, public research, artifact delivery.
- **Limitations:** capability availability and persistence vary by session; repository filesystem access is not assumed.
- **Tool model:** route through the active tool/connector catalog and record actual execution evidence.
- **Persistence model:** separate conversational task state from explicitly durable library artifacts.
- **Approval behavior:** require scoped approval for material external writes and high-impact actions.
- **Startup behavior:** initialize compact dashboard state for substantive tasks.
- **Unsupported behavior:** do not claim repository commands, writes, or connected-source access unless the surface exposes and executes them.
- **Conformance:** candidate; independent bootstrap and propagation proof remain open.

