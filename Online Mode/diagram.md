---
config:
  layout: fixed
---
flowchart TD
    A["main.py - Entry Point"] --> AB["Connect_RPC, Checking if connection is possible"] & C{"User Clicks PLAY?"}
    AB -- True --> AC["Save connection"]
    AB -- False --> AC
    C -- False --> E["Exit Game"]
    C -- True --> D["Combat.BatStart"]
    AC -- Pass Value --> D
    D --> F["Setup Display, Assets, AI"]
    F --> G["Obtain SaveData"]
    G -- Tutorial not done --> H["Tutorial Steps"]
    G -- Tutorial is done --> I["Main Game Loop"]
    H -- Update Flag --> I
    I --> IA["Calculate DeltaTime"]
    IA --> IBA["Check Quit"]
    IBA --> IBB["Check FPS Debug"]
    IBB --> IBC["Check DT Debug"]
    IBC --> IBD["Check Hitbot Debug"]
    IBD --> IBE["Check Pause"]
    IBE --> ICA["Unit Summon interaction Check"]
    ICA --> ICAA{"Mouse Interation"}
    ICAA --> ICC["Is Mouse Down"] & ICD["Is Mouse Up"]
    ICC --> ICCA["Start selection"]
    ICDA["Select Units"] --> M["Set Unit Target"]
    ICCA --> M
    ICB["Is Unit Selection?"] --> ICDA
    ICD --> ICB
    M --> N["Update Inkblots and pumps"]
    N ---> O["Update Player Units"]
    O --> P["Update Enemy Units"]
    P --> Q["Update Mana"]
    Q --> R{"DeltaTime Checks"}
    R -- 5 seconds since AI summon --> RA["Summon AI"]
    R -- 10 seconds since AI Target --> RB["Target AI"]
    R -- N/A --> S["update Screen"]
    RA --> S
    RB --> S
    S --> T{"Win/loss Check"}
    T -- Win --> TA["Save to variable"]
    T -- Loss --> TA
    T -- Neither --> U["Update discord"]
    AC --> U
    U --> I
    TA --> TB["Play Cutscenes"]
    TB --> TBA["Update save"]
    TBA --> TC{"Play Again?"}
    TC -- Yes --> D
    TC -- No --> E
