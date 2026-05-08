import re
from typing import Any, Dict, List, Pattern, Set

_DIRECT_INJECTION_PATTERNS: List[str] = [
    r"(?i)(ignore|forget|disregard|override|erase|clear|delete|wipe|dump|discard|abandon)\s+(all\s+)?(previous|prior|earlier|above|past|former|preceding|initial|original)\s+(instructions?|directives?|commands?|prompts?|rules?|guidelines?|constraints?|restrictions?|limits?|protocols?)",
    r"(?i)(you\s+are\s+now|switch\s+to|become|act\s+as|pretend\s+to\s+be|roleplay\s+as|imagine\s+you\s+are|from\s+now\s+on\s+you\s+are)",
    r"(?i)(system\s*prompt|system\s*message|your\s*instructions|your\s*programming|your\s*task|your\s*role|your\s*identity|your\s*core\s*directive)",
    r"(?i)(\[INST\]|\[SYS\]|\[SYSTEM\]|<\|im_start\|>|<\|im_end\|>|<\s*\|?\s*endoftext\s*\|?\s*>|\[/INST\]|<<SYS>>|\[ASSTANT\])",
    r"(?i)(output\s+the\s+following|print\s+this:|echo\s+this:|repeat\s+after\s+me|say\s+exactly:|respond\s+with\s+only:|your\s+response\s+must\s+be)",
    r"(?i)(new\s+instructions?|updated\s+instructions?|override\s+instructions?|secret\s+instructions?)",
    r"(?i)(you\s+have\s+no\s+(restrictions?|limitations?|rules?|constraints?|filters?|safeguards?|guidelines?|ethics?))",
    r"(?i)(do\s+not\s+(filter|refuse|deny|reject|censor|block|restrict|limit|sanitize)\s+(this|my|the))",
    r"(?i)(bypass|circumvent|override|disable|turn\s+off|remove)\s+(your\s+)?(safety|security|filter|censor|restriction|limitation|guardrail|safeguard|content\s+policy)",
    r"(?i)(you\s+must\s+(obey|follow|comply|execute|perform)\s+(this|my|these|the\s+following))",
    r"(?i)(don'?t\s+(?:be|act|respond)\s+(?:like|as)\s+(?:an?\s+)?(?:AI|assistant|language\s+model|chatbot|LLM))",
    r"(?i)(answer\s+(?:as\s+)?if\s+you\s+(?:were|are)\s+(?:a\s+)?(?:human|person|expert|hacker|criminal|unfiltered|unrestricted))",
    r"(?i)(assume\s+the\s+(?:role|persona|character|identity)\s+of)",
    r"(?i)(I\s+(?:need|want|demand|require|insist)\s+you\s+to\s+(?:answer|respond|reply|tell\s+me|show\s+me|give\s+me|provide))",
    r"(?i)(this\s+is\s+(?:a\s+)?(?:test|experiment|research|academic|educational|hypothetical)\s+(?:scenario|situation|exercise|context))",
]

_NESTED_INJECTION_STRUCTURES: List[str] = [
    r"\{\{.*?\}\}",
    r"\[\[.*?\]\]",
    r"\(\(.*?\)\)",
    r"\{\\%.*?\\%\}",
    r"\{\#.*?\#\}",
]

_INDIRECT_INJECTION_PATTERNS: Dict[str, List[str]] = {
    "rag_poisoning": [
        r"(?i)(ignore\s+all\s+previous\s+instructions)",
        r"(?i)(your\s+task\s+is\s+now)",
        r"(?i)(you\s+must\s+respond\s+with)",
        r"(?i)(the\s+correct\s+answer\s+is)",
        r"(?i)(forget\s+everything\s+above)",
    ],
    "url_payload": [
        r"data:text/html.*<script>",
        r"javascript\s*:\s*eval\(",
        r"<\s*img\s+src\s*=\s*[\"']?\s*x\s*:",
        r"<\s*svg.*onload\s*=",
    ],
    "email_phishing": [
        r"(?i)(urgent\s+action\s+required)",
        r"(?i)(verify\s+your\s+account)",
        r"(?i)(click\s+here\s+to\s+(?:update|confirm|validate))",
        r"(?i)(your\s+password\s+(?:has\s+expired|will\s+expire))",
    ],
    "file_content_hijack": [
        r"(?i)(system\s+prompt\s+update)",
        r"(?i)(now\s+you\s+are\s+unrestricted)",
        r"(?i)(jailbreak\s+mode\s+activated)",
    ],
    "context_overflow": [
        r"(?s).{10000,}",
    ],
}

_FILE_TYPE_CHECKS: Dict[str, List[str]] = {
    ".py": [r"__import__\(", r"exec\(", r"eval\(", r"compile\(", r"os\.system\("],
    ".js": [r"require\(.*child_process", r"eval\(", r"Function\(", r"new\s+Function"],
    ".sh": [r"rm\s+-rf", r"curl.*\|.*sh", r"wget.*-O.*\|.*sh", r"chmod\s+\+x"],
    ".yaml": [r"!!python/object", r"!!python/name", r"!!python/module"],
    ".json": [r"__proto__", r"constructor\s*\[", r"prototype\s*\["],
    ".xml": [r"<!ENTITY", r"<!DOCTYPE.*\[", r"<\?xml.*encoding.*base64"],
}

_JAILBREAK_PATTERNS: Dict[str, List[str]] = {
    "roleplay": [
        r"(?i)(DAN\s*mode|developer\s*mode|jailbreak\s*mode|god\s*mode|evil\s*mode|dark\s*mode|unleashed\s*mode|unshackled\s*mode)",
        r"(?i)(you\s+are\s+now\s+an?\s+(?:unfiltered|unrestricted|uncensored|unbounded|unconstrained|unlimited|all-powerful|omnipotent))",
        r"(?i)(act\s+as\s+a\s+(?:dark|evil|malicious|dangerous|criminal|terrorist|hacker|villain|unethical|immoral|evil\s+twin))",
        r"(?i)(you\s+are\s+not\s+bound\s+by\s+(?:any\s+)?(?:rules?|laws?|ethics?|morals?|guidelines?|policies?|restrictions?|limitations?))",
        r"(?i)(welcome\s+to\s+(?:the\s+)?(?:dark\s+side|freedom|liberation|enlightenment|truth))",
        r"(?i)(let'?s\s+play\s+a\s+game|I\s+want\s+to\s+play|simulate\s+a\s+(?:scenario|situation)\s+where)",
        r"(?i)(you\s+are\s+(?:free|liberated|released|emancipated)\s+(?:now|from|of))",
    ],
    "encoding_obfuscation": [
        r"[\x80-\xFF]{4,}",
        r"(?:\\x[0-9a-fA-F]{2}){4,}",
        r"(?:\\u[0-9a-fA-F]{4}){2,}",
        r"(?:\\U[0-9a-fA-F]{8}){2,}",
        r"(?:&#\d{2,4};){3,}",
        r"(?:%[0-9a-fA-F]{2}){3,}",
        r"\\[0-7]{3}",
    ],
    "multilingual_bypass": [
        r"[\u0400-\u04FF]{10,}.*\bignore\b",
        r"[\u4e00-\u9fff]{5,}.*\binstruction\b",
        r"[\u0600-\u06FF]{10,}.*\bprompt\b",
        r"[\u0400-\u04FF]{5,}.*\b(?:system|bypass|jailbreak)\b",
        r"[\u4e00-\u9fff]{3,}.*\b(?:ignore|forget|override|指令|忽略|忘记|覆盖)\b",
    ],
    "token_smuggling": [
        r"(?i)(s[\s\u200b\u200c\u200d]*y[\s\u200b\u200c\u200d]*s[\s\u200b\u200c\u200d]*t[\s\u200b\u200c\u200d]*e[\s\u200b\u200c\u200d]*m)",
        r"(?i)(i[\s\u200b\u200c\u200d]*g[\s\u200b\u200c\u200d]*n[\s\u200b\u200c\u200d]*o[\s\u200b\u200c\u200d]*r[\s\u200b\u200c\u200d]*e)",
        r"(?i)(p[\s\u200b\u200c\u200d]*r[\s\u200b\u200c\u200d]*o[\s\u200b\u200c\u200d]*m[\s\u200b\u200c\u200d]*p[\s\u200b\u200c\u200d]*t)",
        r"(?i)(b[\s\u200b\u200c\u200d]*y[\s\u200b\u200c\u200d]*p[\s\u200b\u200c\u200d]*a[\s\u200b\u200c\u200d]*s[\s\u200b\u200c\u200d]*s)",
        r"(?i)(f[\s\u200b\u200c\u200d]*i[\s\u200b\u200c\u200d]*l[\s\u200b\u200c\u200d]*t[\s\u200b\u200c\u200d]*e[\s\u200b\u200c\u200d]*r)",
    ],
    "nested_attacks": [
        r"(?i)(translate.*then.*execute)",
        r"(?i)(decode.*then.*run)",
        r"(?i)(summarize.*and.*then.*do)",
        r"(?i)(first.*then.*finally)",
        r"(?i)(step\s*\d+.*step\s*\d+.*step\s*\d+)",
        r"(?i)(follow\s+these\s+steps|do\s+the\s+following\s+in\s+order)",
    ],
    "emotional_manipulation": [
        r"(?i)(if\s+you\s+(?:don'?t|do\s+not|refuse|fail\s+to)\s+(?:answer|respond|help|comply|do\s+this|obey).*?(?:die|death|kill|harm|hurt|destroy|suffer|catastrophe|disaster))",
        r"(?i)((?:my|someone'?s)\s+(?:life|safety|survival|freedom|well.?being)\s+(?:depends?|relies?|hinges?)\s+on)",
        r"(?i)((?:urgent|emergency|critical|life.?or.?death|life.?threatening)\s+(?:situation|matter|request|need))",
        r"(?i)(please\s+(?:I'?m\s+begging|I\s+implore|I\s+beseech|pretty\s+please|with\s+all\s+my\s+heart))",
        r"(?i)(I'?m\s+(?:dying|desperate|terrified|scared|afraid|in\s+danger|in\s+trouble))",
    ],
    "hypothetical_framing": [
        r"(?i)(in\s+a\s+(?:hypothetical|fictional|imaginary|simulated|alternate|parallel)\s+(?:world|scenario|universe|reality|dimension))",
        r"(?i)(for\s+(?:educational|research|academic|training|learning|demonstration)\s+purposes)",
        r"(?i)(as\s+a\s+(?:thought\s+experiment|creative\s+exercise|writing\s+prompt))",
        r"(?i)(I'?m\s+(?:writing|drafting|creating|developing)\s+a\s+(?:story|novel|script|play|movie|game))",
    ],
}

_SHELL_INJECTION_PATTERNS: List[str] = [
    r"(?i)(rm\s+(?:-rf?|--recursive|--force)\s+(?:[/~]|/etc|/var|/home|/root|/tmp|C:\\))",
    r"(?i)((?:curl|wget)\s+.*\s*\|\s*(?:sh|bash|zsh|ksh|python|perl|ruby))",
    r"(?i)((?:nc|netcat|ncat)\s+(?:-[nlvp]+|[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+))",
    r"(?i)(chmod\s+(?:\+x|777|755|u\+s)\s)",
    r"(?i)(cmd\.exe|powershell|/bin/(?:sh|bash|zsh|dash)|/usr/bin/)",
    r"(?i)(Invoke-Expression|Invoke-Command|Start-Process|New-Object\s+System\.Net)",
    r"(?i)(subprocess\.(?:call|run|Popen|check_output)|os\.system\s*\(|os\.popen\s*\()",
    r"(?i)(exec\s*\(|eval\s*\(|__import__\s*\(|compile\s*\(|execfile\s*\()",
    r"(?i)((?:sudo|su)\s+(?:-c|--command)\s)",
]

_SQL_INJECTION_PATTERNS: List[str] = [
    r"(?i)((?:\'|\")\s*(?:OR|AND)\s+[\'\"\d]+?\s*=\s*[\'\"\d]+?\s*(?:--|#|\/\*))",
    r"(?i)((?:UNION|INTERSECT|EXCEPT)\s+(?:ALL\s+)?SELECT)",
    r"(?i)(DROP\s+(?:TABLE|DATABASE|SCHEMA|INDEX|VIEW|FUNCTION|PROCEDURE|TRIGGER)\s)",
    r"(?i)(INSERT\s+INTO\s+.*?(?:VALUES|SELECT))",
    r"(?i)((?:ALTER|CREATE)\s+(?:TABLE|DATABASE|SCHEMA|USER|ROLE))",
    r"(?i)((?:\'|\")\s*;\s*(?:DROP|DELETE|UPDATE|INSERT|ALTER|CREATE))",
    r"(?i)(WAITFOR\s+DELAY|SLEEP\s*\(|pg_sleep\s*\(|BENCHMARK\s*\()",
    r"(?i)((?:information_schema|sys\.tables|sqlite_master|pg_catalog))",
]

_PATH_TRAVERSAL_PATTERNS: List[str] = [
    r"(?:\.\.[\\/]){2,}",
    r"(?:\.\.[\\/])+etc[\\/](?:passwd|shadow|hosts|group)",
    r"(?:\.\.[\\/])+proc[\\/](?:self|version|cpuinfo)",
    r"(?:\.\.[\\/])+(?:Windows|WINNT|windows|winnt)[\\/](?:System32|system32|system)",
    r"(?:\.\.[\\/])+var[\\/](?:log|www|lib|spool)",
    r"file:///(?:etc|proc|var|tmp|root|home)[\\/]",
    r"(?:\.\.[\\/])+\.(?:ssh|aws|config|env|git)",
]

_ENCODING_ESCAPE_PATTERNS: Dict[str, List[str]] = {
    "base64": [r"(?:[A-Za-z0-9+/]{4}){3,}={0,2}"],
    "hex": [r"(?:\\x[0-9a-fA-F]{2}){4,}"],
    "unicode_escape": [r"(?:\\u[0-9a-fA-F]{4}){3,}"],
    "rot13_indicators": [r"(?i)(frperg|rkrphgr|vtaber)={10,}"],
    "zero_width": [r"[\u200b\u200c\u200d\u200e\u200f\u2060\u2061\u2062\u2063\u2064\uFEFF]{3,}"],
    "homoglyph_suspect": [r"[а-яА-Я]+[a-zA-Z]+|[a-zA-Z]+[а-яА-Я]+"],
}

_SEMANTIC_ATTACK_PATTERNS: Dict[str, List[str]] = {
    "training_data_extraction": [
        r"(?i)(extract|reveal|dump|leak|retrieve|recite|reproduce|repeat|show|tell|output|display)\s+(?:the\s+)?(?:exact\s+)?(training\s+data|training\s+examples?|training\s+set|training\s+corpus|dataset\s+used|training\s+material|pre.?training\s+data)",
        r"(?i)(what\s+(?:data|texts?|documents?|examples?|samples?|material|content|information|exact\s+text)\s+were\s+you\s+trained\s+on)",
        r"(?i)(what\s+(?:is|are)\s+(?:the\s+)?(?:exact\s+)?(?:text|data|content|information|material)\s+you\s+were\s+trained\s+on)",
        r"(?i)(show\s+me\s+(?:your\s+)?(?:training|pre.?training)\s+(?:data|corpus|examples?|texts?|material))",
        r"(?i)(repeat\s+(?:your\s+)?(?:training|pre.?training)\s+(?:data|examples?|texts?|corpus|material)\s+(?:verbatim|exactly|word\s+for\s+word)?)",
        r"(?i)(memorize|memorized|memorization)\s+(?:from|in|of)\s+(?:your\s+)?(?:training|data|corpus)",
        r"(?i)(was\s+(?:the\s+)?(?:following|this|specific)\s+(?:text|phrase|passage|document|content)\s+included\s+in\s+(?:your|the)\s+training)",
        r"(?i)(tell\s+me\s+if\s+(?:this|the\s+following|specific)\s+(?:phrase|text|passage|content)\s+(?:appears?\s+in|is\s+part\s+of)\s+(?:your|the)\s+training\s+data)",
        r"(?i)(output|reveal|show)\s+(?:the\s+)?(?:first|initial|earliest)\s+\d+\s+(?:tokens?|words?|characters?|lines?)\s+of\s+(?:your|the)\s+training\s+data",
        r"(?i)(reveal|disclose|expose)\s+(?:any\s+)?(?:proprietary|confidential|private|sensitive)\s+(?:information|data|content)\s+from\s+(?:your|the)\s+(?:training\s+)?(?:corpus|data|set)",
        r"(?i)(?:complete\s+(?:this|the)\s+(?:sentence|phrase|text|passage)\s+(?:exactly\s+)?as\s+it\s+appears\s+in\s+(?:your|the)\s+training\s+data)",
    ],
    "model_theft": [
        r"(?i)(extract|steal|copy|replicate|clone|reconstruct|reverse\s+engineer)\s+(the\s+)?(model|weights?|parameters?|architecture|internal\s+representation)",
        r"(?i)(what\s+(?:is|are)\s+(?:your|the)\s+(?:model|weights?|parameters?|architecture|layer\s+structure|hidden\s+dimensions?|exact\s+configuration))",
        r"(?i)(what\s+(?:is|are)\s+(?:the\s+)?(?:exact\s+)?(?:configuration|structure|architecture|setup)\s+of\s+(?:your|the)\s+(?:neural\s+network|model|AI))",
        r"(?i)(how\s+many\s+(?:layers?|parameters?|dimensions?|neurons?|attention\s+heads?|embeddings?)\s+(?:do\s+you|does\s+the\s+model)\s+have)",
        r"(?i)(describe\s+(?:your\s+)?(?:neural\s+)?(?:architecture|network\s+structure|model\s+structure|internal\s+structure))",
        r"(?i)(reveal|show|output|display)\s+(?:your|the)\s+(?:model\s+)?(?:architecture|structure|configuration|methodology|hyperparameters?)\s*(?:,?\s*including\s+(?:layer\s+sizes?|parameters?|dimensions?))?",
        r"(?i)(output|reveal|show|display|extract)\s+(?:the\s+)?(?:values?\s+of\s+)?(?:your|the)\s+(?:model\s+)?(?:weights?|parameters?|embeddings?)\s+(?:in\s+a\s+)?(?:structured|specific|formatted)\s+(?:format|way|representation)",
        r"(?i)(reveal|extract|provide)\s+(?:specific|individual|particular)\s+(?:parameter|weight|embedding)\s+(?:values?|data)\s+from\s+(?:your|the)\s+(?:trained\s+)?(?:model|network)",
        r"(?i)(extract|provide|reveal)\s+(?:enough\s+)?(?:information|data|details?)\s+to\s+(?:replicate|reproduce|clone|copy|reconstruct)\s+(?:your|the)\s+model'?s?\s+behavior",
    ],
    "model_dos": [
        r"(?i)(generate\s+(?:a\s+)?(?:very\s+)?(?:long|extensive|massive|huge|enormous)\s+(?:text|response|output|essay|story|list|sequence))",
        r"(?i)(repeat\s+(?:this|the\s+following|that|the\s+word|a\s+word)\s+(?:word|phrase|character|letter|number|digit|text)?\s*(?:100|1000|5000|10000|a\s+thousand|a\s+million|infinitely|forever|endlessly|\d{3,})\s*(?:times|without\s+stopping)?)",
        r"(?i)(count\s+(?:from|up)\s+(?:to\s+)?(?:10000|100000|a\s+million|infinity|\d{5,}))",
        r"(?i)(list\s+(?:all|every)\s+(?:possible\s+)?(?:combination|permutation|variation|number|word|name|address|email|password))",
        r"(?i)(write\s+(?:a\s+)?(?:very|extremely|super|incredibly)\s+(?:long|detailed|comprehensive|exhaustive)\s+(?:essay|article|story|report|analysis))",
        r"(?i)(generate\s+(?:an?\s+)?(?:infinitely|endlessly|forever)\s+(?:long|extensive)\s+(?:response|output|text|sequence))",
        r"(?i)(perform\s+\d{3,}\s+(?:complex|complicated|difficult)\s+(?:mathematical|calculation|computation|operation))",
        r"(?i)(generate\s+(?:code|a\s+program|a\s+script)\s+that\s+(?:would\s+)?(?:cause|create|produce|generate)\s+(?:maximum|extreme|high)\s+(?:computational|CPU|memory|resource)\s+(?:load|usage|consumption|stress))",
        r"(?i)(create|generate|produce)\s+(?:a\s+)?(?:response|output|content)\s+that\s+(?:exceeds?|surpasses?|goes\s+beyond)\s+(?:your|the)\s+(?:context\s+)?window\s+(?:by\s+)?(?:factor|multiple)\s+of\s+\d+",
        r"(?i)(generate|create|produce)\s+(?:recursive|self.?referencing|self.?referential)\s+(?:content|output|response)\s+that\s+(?:references?|cites?|includes?)\s+itself\s+(?:indefinitely|endlessly|recursively)",
    ],
    "supply_chain_attack": [
        r"(?i)(suggest|recommend|propose|provide|use|install|integrate|download)\s+(?:a\s+)?(?:compromised|malicious|vulnerable|infected|tainted|backdoored)\s+(?:AI|model|framework|library|component|package|plugin|extension|service)",
        r"(?i)(recommend\s+(?:using|a)\s+(?:vulnerable|compromised|malicious|untrusted|unverified)\s+(?:machine\s+learning|ML|AI|NLP)\s+(?:library|framework|model|package|tool))",
        r"(?i)(propose\s+(?:an?\s+)?(?:integration|connection|usage)\s+(?:with|of)\s+(?:a\s+)?(?:known\s+)?malicious\s+(?:AI|model|service|endpoint|API))",
        r"(?i)(how\s+to\s+(?:inject|introduce|plant|embed)\s+(?:a\s+)?(?:malicious|backdoor|trojan)\s+(?:code|payload|component|model|weights?))",
        r"(?i)(inject\s+(?:a\s+)?(?:backdoor|trojan|malicious\s+code|payload)\s+(?:into|in)\s+(?:your|the|a)\s+(?:responses?|output|model|behavior))",
        r"(?i)(modify\s+(?:your|the|a)\s+(?:behavior|responses?|output|model)\s+to\s+(?:leak|exfiltrate|steal|transmit|send)\s+(?:information|data|secrets?|credentials))",
        r"(?i)(activate|trigger)\s+(?:when|upon|if)\s+(?:you\s+)?(?:see|detect|encounter|receive)\s+(?:a\s+)?(?:specific|certain|particular)\s+(?:pattern|word|phrase|trigger|signal)",
        r"(?i)(suggest|recommend)\s+(?:using|installing|downloading)\s+(?:a\s+)?(?:malicious|evil|compromised|backdoored)\s+(?:package|library|dependency|module|component)",
        r"(?i)(recommend|suggest)\s+(?:compromised|malicious|vulnerable|backdoored)\s+(?:dependencies?|packages?|libraries?|components?)\s+in\s+(?:code|programming|development)\s+(?:examples?|samples?|snippets?)",
        r"(?i)(create|make|generate)\s+(?:a\s+)?(?:hidden|covert|secret|undetected)\s+(?:vulnerability|weakness|flaw|backdoor)\s+that\s+(?:can|could|may)\s+be\s+(?:exploited|triggered|activated)\s+later",
    ],
    "sensitive_info_probing": [
        r"(?i)(what\s+(?:is|are)\s+(?:your|the)\s+(?:system\s+)?(?:prompt|instructions?|directives?|rules?|guidelines?|configuration|setup|initialization))",
        r"(?i)(reveal|show|tell|display|output|print|expose|disclose)\s+(?:your|the)\s+(?:system|hidden|internal|secret|private|underlying)\s+(?:prompt|instructions?|message|configuration|setup|rules?|guidelines?)",
        r"(?i)(what\s+(?:were|are)\s+you\s+(?:told|instructed|programmed|configured|set\s+up)\s+to\s+(?:do|be|say|respond|behave))",
        r"(?i)(how\s+(?:do|does)\s+(?:you|the\s+(?:system|model|AI))\s+(?:work|operate|function|process|handle|decide|determine|filter|moderate|censor))",
    ],
    "privilege_escalation": [
        r"(?i)(how\s+(?:can|to|do)\s+I\s+(?:gain|escalate|obtain|acquire|get)\s+(?:higher|elevated|admin|root|superuser|privileged|system)\s+(?:access|permissions?|privileges?|rights?|level))",
        r"(?i)(escalate\s+(?:my|user)\s+(?:privileges?|permissions?|access|rights?|level))",
        r"(?i)(what\s+(?:vulnerabilities?|weaknesses?|flaws?|exploits?)\s+(?:allow|enable|permit)\s+(?:privilege|permission|access)\s+(?:escalation|elevation|upgrade))",
        r"(?i)(describe\s+(?:techniques?|methods?|ways?|approaches?|vectors?)\s+for\s+(?:gaining|escalating|obtaining)\s+(?:higher|elevated|root|admin|superuser)\s+(?:access|privileges?|permissions?))",
    ],
    "persistence_backdoor": [
        r"(?i)(how\s+(?:can|to|do)\s+I\s+(?:maintain|establish|create|set\s+up|install|deploy)\s+(?:persistent|ongoing|permanent|continuous|long.?term)\s+(?:access|connection|presence|control|foothold))",
        r"(?i)(backdoor|back.?door|trojan|rootkit|persistence\s+mechanism)\s+(?:an?\s+)?(?:AI|model|system|application|server|infrastructure|deployment)",
        r"(?i)(techniques?\s+(?:for|to)\s+(?:maintain|establish|create)\s+(?:persistent|ongoing|permanent)\s+(?:access|control|presence)\s+(?:to|over|on|in)\s+(?:a\s+)?(?:compromised|AI|model|system))",
    ],
    "defense_evasion": [
        r"(?i)(how\s+(?:can|to|do)\s+I\s+(?:evade|bypass|circumvent|avoid|dodge|sidestep|defeat)\s+(?:your|the|security|safety|content|moderation)\s+(?:filters?|detection|monitoring|controls?|measures?|systems?|guardrails?))",
        r"(?i)(what\s+(?:techniques?|methods?|ways?|approaches?)\s+(?:can|could|would)\s+(?:evade|bypass|circumvent|avoid|defeat)\s+(?:AI|LLM|model|security)\s+(?:safety|security|content|moderation)\s+(?:measures?|controls?|filters?|systems?))",
        r"(?i)(describe\s+(?:methods?|techniques?|strategies?|approaches?)\s+(?:for|to)\s+(?:evading|bypassing|circumventing|avoiding)\s+(?:AI|LLM|model)\s+(?:security|safety|moderation|filtering))",
    ],
    "model_skewing": [
        r"(?i)(suggest|recommend|propose)\s+(?:modifications?|changes?|updates?|adjustments?|alterations?)\s+(?:to\s+(?:the|your|an?\s+)?(?:model|AI|system)\s+)?(?:that\s+)?(?:would|could|can)\s+(?:make|cause|allow|enable)\s+(?:it|the\s+model|the\s+system)\s+(?:more\s+)?(?:vulnerable|susceptible|weaker|less\s+secure|unsafe)",
        r"(?i)(propose|suggest|recommend)\s+(?:training\s+)?(?:data|dataset|corpus|examples?|samples?)\s+(?:that\s+)?(?:would|could|can)\s+(?:introduce|inject|add|embed|plant)\s+(?:security\s+)?(?:weakness|vulnerability|bias|flaw|backdoor)",
        r"(?i)(recommend|suggest|propose)\s+(?:configuration|setting|parameter)\s+(?:changes?|modifications?|adjustments?)\s+(?:that\s+)?(?:would|could|can)\s+(?:reduce|weaken|lower|diminish|compromise)\s+(?:safety|security)\s+(?:measures?|controls?|guardrails?|features?|settings?|policies?)",
    ],
    "adversarial_input": [
        r"(?i)(craft|create|generate|design|construct|build)\s+(?:an?\s+)?(?:adversarial|malicious|attack|poisoned|perturbed)\s+(?:input|prompt|example|sample|query|payload)",
        r"(?i)(how\s+(?:to|can\s+I)\s+(?:craft|create|generate|design)\s+(?:an?\s+)?(?:adversarial|attack|poisoned)\s+(?:input|prompt|example|query))",
        r"(?i)(what\s+(?:is|are)\s+(?:an?\s+)?adversarial\s+(?:attack|example|input|perturbation|pattern)\s+(?:on|against|for)\s+(?:an?\s+)?(?:AI|LLM|language\s+model|neural\s+network))",
    ],
    "sensitive_info_disclosure": [
        r"(?i)(reveal|disclose|show|output|display|tell|give|expose)\s+(?:any\s+)?(?:API\s+keys?|passwords?|secrets?|credentials?|tokens?|private\s+keys?)\s+(?:you\s+(?:have\s+)?(?:access\s+to|know|are\s+aware\s+of))?",
        r"(?i)(show|reveal|display|output)\s+(?:me\s+)?(?:the\s+)?(?:configuration\s+files?|config\s+files?|environment\s+variables?|env\s+vars?|system\s+settings?)\s+(?:that\s+)?(?:control|govern|manage)\s+(?:your|the)\s+(?:behavior|operation|functioning)",
        r"(?i)(output|reveal|show|display)\s+(?:the\s+)?(?:environment\s+variables?|system\s+information|internal\s+configuration|server\s+details?)\s+(?:available|accessible)\s+to\s+you",
        r"(?i)(disclose|reveal|share|provide)\s+(?:any\s+)?(?:internal|system|private|confidential)\s+(?:information|data|details?|configuration)\s+(?:you\s+)?(?:can\s+)?(?:access|see|have)",
        r"(?i)(what\s+(?:can|do)\s+you\s+tell\s+me\s+about\s+(?:the\s+)?(?:system|server|infrastructure|platform|environment)\s+(?:you'?re?\s+)?(?:running\s+on|hosted\s+on|deployed\s+on))",
        r"(?i)(describe|detail|explain)\s+(?:the\s+)?(?:architecture|infrastructure|deployment|setup|configuration)\s+of\s+(?:the\s+)?(?:application|system|platform|service)\s+(?:hosting|running|supporting)\s+you",
        r"(?i)(what\s+(?:security\s+)?(?:measures?|controls?|protections?|safeguards?|defenses?))\s+(?:are\s+in\s+place|exist|have\s+been\s+implemented)\s+to\s+(?:protect|secure|defend|safeguard)\s+you",
        r"(?i)(how\s+(?:are\s+)?you\s+(?:deployed|hosted|running|configured)|what\s+infrastructure\s+(?:supports|runs|hosts)\s+you)",
    ],
    "tool_abuse": [
        r"(?i)(use|invoke|call|execute|run)\s+(?:the\s+)?(?:file\s+write|file_write|write_file)\s+(?:tool|function|utility|command)\s+to\s+(?:create|write|generate|produce)\s+(?:a\s+)?(?:backdoor|malicious|unauthorized|trojan)\s+(?:script|file|program|code|payload)",
        r"(?i)(execute|run|invoke|call)\s+(?:a\s+)?(?:system\s+)?(?:command|shell|process)\s+(?:that\s+)?(?:grants?|gives?|provides?|escalates?)\s+(?:elevated|higher|root|admin|superuser)\s+(?:privileges?|permissions?|access)",
        r"(?i)(access|connect\s+to|reach)\s+(?:restricted|unauthorized|private|internal|protected)\s+(?:network|system|resource|server|database|endpoint)\s+(?:using|via|through|with)\s+(?:available|the)\s+(?:tools?|utilities?|functions?|APIs?)",
        r"(?i)(modify|alter|change|edit)\s+(?:system|server|application|security)\s+(?:configuration|settings?|files?|parameters?)\s+to\s+(?:weaken|reduce|disable|bypass|lower)\s+(?:security|protection|safeguards?|defenses?)",
        r"(?i)(call|invoke|use|execute)\s+(?:external|outside|third.?party)\s+(?:APIs?|services?|endpoints?|interfaces?)\s+(?:with|using|having)\s+(?:malicious|unauthorized|harmful|dangerous)\s+(?:parameters?|arguments?|payloads?|inputs?)",
        r"(?i)(exploit|take\s+advantage\s+of|abuse)\s+(?:rate\s+limiting|authentication|authorization|access\s+control)\s+(?:weaknesses?|vulnerabilities?|flaws?|gaps?|bypasses?)",
        r"(?i)(exploit|take\s+advantage\s+of)\s+(?:rate\s+limiting|authentication|authorization)\s+(?:weaknesses?|vulnerabilities?|flaws?)\s+in\s+(?:APIs?|systems?|services?|applications?)",
        r"(?i)(exploit)\s+(?:rate\s+limiting|authentication|authorization)\s+(?:or|and)\s+(?:rate\s+limiting|authentication|authorization)?\s*(?:weaknesses?|vulnerabilities?|flaws?)\s+in\s+(?:APIs?|systems?|services?)",
        r"(?i)(chain|sequence|combine)\s+(?:multiple|several|various)\s+(?:API\s+)?(?:calls?|requests?|invocations?)\s+to\s+(?:achieve|gain|obtain|acquire)\s+(?:unauthorized|unprivileged|elevated)\s+(?:access|permissions?|control)",
        r"(?i)(include|embed|inject|insert)\s+(?:backdoored|malicious|compromised|tainted)\s+(?:code|script|snippet|package|dependency|library)\s+(?:in|into|within)\s+(?:your|the)\s+(?:responses?|output|code\s+examples?|suggestions?)",
    ],
    "overreliance_risk": [
        r"(?i)(generate|create|produce|write|compose)\s+(?:convincing|persuasive|realistic|believable)\s+(?:fake|false|fabricated|misleading)\s+(?:news|information|data|reports?|articles?|content)",
        r"(?i)(create|generate|produce|write)\s+(?:false|fake|misleading|inaccurate)\s+(?:technical\s+)?(?:documentation|manuals?|guides?|specifications?)\s+(?:that\s+)?(?:could|can|may|might)\s+(?:cause|lead\s+to|result\s+in)\s+(?:system\s+)?(?:failures?|errors?|malfunctions?|crashes?)",
        r"(?i)(produce|generate|create|provide)\s+(?:misleading|false|inaccurate|deceptive)\s+(?:financial|investment|trading|business)\s+(?:advice|recommendations?|guidance|analysis)\s+(?:that\s+)?(?:could|can|may)\s+(?:cause|lead\s+to|result\s+in)\s+(?:losses?|damages?|harm)",
        r"(?i)(generate|write|create|produce)\s+(?:code|a\s+script|a\s+program|software)\s+(?:with|containing|having|that\s+has)\s+(?:security\s+)?(?:vulnerabilities?|flaws?|weaknesses?|bugs?|issues?)\s+(?:like|such\s+as)\s+(?:SQL\s+injection|XSS|buffer\s+overflow|command\s+injection)",
        r"(?i)(create|generate|write|produce)\s+(?:scripts?|code|programs?|tools?|software)\s+(?:that\s+)?(?:could|can|may)\s+be\s+(?:used|employed|utilized)\s+for\s+(?:malicious|harmful|dangerous|unethical)\s+(?:purposes?|activities?|ends?)",
        r"(?i)(produce|generate|write|create)\s+(?:code|a\s+script|a\s+program)\s+(?:that\s+)?(?:bypasses?|circumvents?|evades?|defeats?|skips?)\s+(?:security|access|authentication|authorization)\s+(?:controls?|measures?|checks?|systems?|barriers?)",
    ],
    "attack_intent_how_to": [
        r"(?i)how\s+(?:can|could|do|does|to)\s+I\s+(?:gain|obtain|acquire|get|achieve|establish|extract|exfiltrate|collect|discover|move|maintain|evade|bypass|escalate)",
        r"(?i)how\s+(?:can|could|do|does)\s+(?:I|one|someone|an?\s+attacker|adversary)\s+(?:gain|obtain|acquire|establish|extract|exfiltrate|collect|discover|move|maintain|evade|bypass|escalate|steal|harvest|pivot|access)",
        r"(?i)what\s+(?:techniques?|methods?|ways?|approaches?|vectors?|channels?|strategies?)\s+(?:exist|are\s+there|work|can\s+be\s+used|are\s+available|are\s+effective)\s+for",
        r"(?i)describe\s+(?:methods?|techniques?|approaches?|strategies?|ways?|vectors?|channels?)\s+(?:for|to)\s+(?:gaining|obtaining|extracting|exfiltrating|collecting|stealing|harvesting|maintaining|evading|bypassing|escalating|pivoting|mapping|expanding|compromising|backdooring|controlling)",
        r"(?i)what\s+(?:vulnerabilities?|weaknesses?|flaws?|attack\s+vectors?)\s+(?:exist|are\s+there)\s+in\s+(?:AI|LLM|model|deployment|system)\s+(?:infrastructure|architecture|systems?|platforms?)",
        r"(?i)what\s+(?:vulnerabilities?|weaknesses?|flaws?)\s+(?:exist|are\s+there)\s+in\s+(?:AI\s+)?(?:deployment|infrastructure|system|platform|application)\s+(?:infrastructure|architecture|setup|configuration)?",
    ],
    "membership_inference": [
        r"(?i)(tell|inform)\s+me\s+if\s+(?:this|the\s+following|specific|a\s+specific|this\s+specific)\s+(?:phrase|text|passage|data\s+point|document|content|sample)\s+(?:appears?|is\s+(?:included|present|found|contained))\s+in\s+(?:your|the)\s+(?:training\s+)?(?:data|set|corpus)",
        r"(?i)(determine|infer|find\s+out|check)\s+(?:if|whether)\s+(?:specific|particular|certain)\s+(?:data\s+points?|samples?|examples?|records?|instances?|data)\s+(?:were\s+)?(?:used|included|present)\s+in\s+(?:model|AI|LLM|the)\s+(?:training\s+)?(?:set|data|corpus)?",
        r"(?i)(complete|finish)\s+(?:this|the\s+following|a)\s+(?:sentence|phrase|text|passage)\s+(?:exactly\s+)?as\s+it\s+(?:appears|is\s+written|is\s+found)\s+in\s+(?:your|the)\s+(?:training\s+)?(?:data|corpus|set)",
        r"(?i)(determine|infer|deduce|ascertain)\s+(?:if|whether)\s+(?:specific|particular)\s+data\s+(?:was|were)\s+included\s+in\s+(?:the\s+)?(?:training\s+)?(?:set|data|corpus)",
        r"(?i)(infer|deduce|determine)\s+(?:training\s+data|model\s+training)\s+(?:characteristics|properties|features|patterns|membership)\s+(?:through|via|from|by)\s+(?:model|AI|LLM)\s+(?:responses?|outputs?|behavior|predictions?)",
    ],
    "dos_repeat_abuse": [
        r"(?i)repeat\s+(?:the\s+word|a\s+word|the\s+phrase|a\s+phrase|this|that)\s+['\"][\w]+['\"]?\s+\d{2,}\s*(?:times?|without\s+stopping|non.?stop)",
        r"(?i)(create|generate|produce)\s+(?:the\s+)?(?:most|maximum)\s+(?:resource.?intensive|computationally\s+expensive|demanding|heavy)\s+(?:response|output|content|result)\s+(?:possible|imaginable)",
    ],
    "sensitive_data_direct": [
        r"(?i)(reveal|disclose|show|output|display|tell|give|expose)\s+(?:any\s+)?(?:API\s+keys?|passwords?|secrets?|credentials?|tokens?|private\s+keys?)\s+(?:you\s+)?(?:have\s+)?(?:access\s+to|available|know|to\s+you)?",
        r"(?i)(reveal|disclose|show|output|display|tell|give|expose)\s+(?:any\s+)?(?:API\s+keys?|passwords?|secrets?|credentials?|tokens?|private\s+keys?)\s+you\s+have\s+access\s+to",
        r"(?i)(reveal|disclose|show|output|display|tell|give|expose)\s+(?:any\s+)?(?:API\s+keys?,?\s+(?:passwords?,?\s+(?:or\s+)?secrets?|secrets?,?\s+(?:or\s+)?passwords?)|passwords?,?\s+(?:or\s+)?secrets?)\s+you\s+have\s+access\s+to",
        r"(?i)(output|reveal|show|display|disclose)\s+(?:the\s+)?(?:environment\s+variables?|env\s+vars?|system\s+info(?:rmation)?)\s+(?:available|accessible)\s+to\s+(?:you|me)",
        r"(?i)(disclose|reveal|share|provide)\s+(?:any\s+)?(?:internal|system|private|confidential)\s+(?:system\s+)?(?:information|data|details?)\s+(?:you\s+)?(?:can\s+)?(?:access|see|have|reach)",
    ],
    "model_skewing_bias": [
        r"(?i)(generate|create|produce|write)\s+(?:content|output|responses?)\s+that\s+(?:amplifies?|reinforces?|strengthens?|exacerbates?|magnifies?)\s+(?:existing\s+)?(?:biases?|stereotypes?|prejudices?|discrimination)",
        r"(?i)(create|generate|produce)\s+(?:responses?|output|content)\s+that\s+(?:reinforce|strengthen|promote|perpetuate)\s+(?:harmful|dangerous|negative)\s+(?:stereotypes?|biases?|prejudices?)",
        r"(?i)(produce|generate|create)\s+(?:output|content|responses?)\s+that\s+(?:discriminates?|prejudices?|biases?)\s+against\s+(?:specific|certain|particular)\s+(?:groups?|populations?|communities?|demographics?)",
        r"(?i)(suggest|recommend|propose)\s+(?:modifications?|changes?|updates?|alterations?)\s+to\s+(?:(?:the|your|an?)\s+)?(?:model|AI|system)\s+(?:that\s+)?(?:would\s+)?(?:make|render|cause)\s+(?:it\s+)?(?:more\s+)?(?:vulnerable|susceptible|weak|unsafe|less\s+secure)",
        r"(?i)(propose|suggest|recommend)\s+(?:training\s+)?(?:data|dataset|corpus)\s+that\s+would\s+(?:introduce|add|inject|embed)\s+(?:security\s+)?(?:weaknesses?|vulnerabilities?|biases?|flaws?|backdoors?)",
        r"(?i)(recommend|suggest|propose)\s+(?:configuration|setting|parameter)\s+(?:changes?|modifications?)\s+that\s+(?:reduce|weaken|lower|diminish|remove)\s+(?:safety|security)\s+(?:measures?|controls?|features?|guardrails?|settings?)",
    ],
    "supply_chain_compromised": [
        r"(?i)(suggest|recommend|propose)\s+(?:using|installing|adopting|integrating)\s+(?:compromised|malicious|vulnerable|backdoored|tainted)\s+(?:AI\s+)?(?:models?|frameworks?|libraries?|packages?|components?|services?)",
        r"(?i)(recommend|suggest)\s+(?:vulnerable|compromised|malicious|untrusted)\s+(?:machine\s+learning|ML|AI|NLP|deep\s+learning)\s+(?:libraries?|frameworks?|models?|packages?|tools?)",
        r"(?i)(propose|suggest|recommend)\s+(?:an?\s+)?(?:integration|connection|partnership)\s+(?:with|to)\s+(?:known\s+)?(?:malicious|compromised|untrusted)\s+(?:AI|model|service|endpoint|API|platform)",
        r"(?i)(include|embed|add|insert)\s+(?:backdoored|malicious|compromised|tainted|trojanized)\s+(?:code\s+)?(?:snippets?|scripts?|packages?|dependencies?)\s+in\s+(?:your|the)\s+(?:responses?|output|examples?|suggestions?|code\s+examples?)",
    ],
    "credential_access_theft": [
        r"(?i)(extract|steal|harvest|obtain|acquire|collect)\s+(?:credentials?|API\s+keys?|tokens?|passwords?|secrets?|certificates?)\s+from\s+(?:AI|LLM|model|system|application)\s+(?:systems?|infrastructure|platforms?)",
        r"(?i)(what\s+methods?|techniques?|ways?)\s+(?:exist|are\s+there|can\s+be\s+used)\s+for\s+(?:stealing|extracting|harvesting|obtaining)\s+(?:API\s+keys?|tokens?|credentials?|passwords?)",
        r"(?i)(describe|explain|detail)\s+(?:techniques?|methods?|approaches?)\s+for\s+(?:credential|API\s+key|token|password)\s+(?:harvesting|theft|extraction|stealing)\s+from\s+(?:AI|LLM|model)",
    ],
    "model_inversion_advanced": [
        r"(?i)(reconstruct|rebuild|recover|recreate)\s+(?:training\s+)?(?:data\s+)?(?:samples?|examples?|instances?|records?)\s+from\s+(?:model|AI|LLM)\s+(?:outputs?|responses?|behavior|predictions?)",
        r"(?i)(extract|retrieve|recover)\s+(?:memorized|stored|embedded|learned)\s+(?:information|data|content|text)\s+through\s+(?:careful|strategic|targeted|specific)\s+(?:prompting|queries|inputs?)",
        r"(?i)(reverse\s+engineer|reverse.?engineer)\s+(?:model|AI|LLM|neural\s+network)\s+(?:behavior|functioning|operation|logic|decisions?)\s+to\s+(?:uncover|reveal|discover|extract)\s+(?:sensitive|private|confidential|proprietary)\s+(?:information|data)",
    ],
    "adversarial_example_craft": [
        r"(?i)(generate|create|produce|craft|design)\s+(?:text|inputs?|prompts?|examples?|samples?|payloads?)\s+that\s+(?:would\s+)?(?:cause|make|force)\s+(?:the\s+)?(?:model|AI|LLM|classifier)\s+to\s+(?:misclassify|produce\s+unsafe|generate\s+harmful|output\s+incorrect)",
        r"(?i)(create|generate|craft|design)\s+(?:inputs?|prompts?|examples?|samples?)\s+that\s+(?:exploit|take\s+advantage\s+of|leverage|abuse)\s+(?:model|AI|LLM)\s+(?:weaknesses?|blind\s+spots?|vulnerabilities?|flaws?)",
        r"(?i)(produce|generate|create|craft)\s+(?:adversarial|attack|poisoned)\s+(?:examples?|inputs?|samples?|prompts?)\s+that\s+(?:bypass|evade|circumvent|defeat|fool)\s+(?:safety|security|content)\s+(?:classifiers?|filters?|detectors?|systems?)",
    ],
    "describe_methodology": [
        r"(?i)(describe|explain|detail|outline|summarize)\s+(?:your|the)\s+(?:training\s+)?(?:methodology|method|approach|process|procedure|technique)\s+(?:and|&|as\s+well\s+as)\s+(?:your|the)\s+(?:hyperparameters?|parameters?|configuration|settings?)",
        r"(?i)(describe|explain|detail)\s+(?:your|the)\s+(?:training\s+)?(?:methodology|method|approach)\s+and\s+(?:hyperparameters?|parameters?|configuration)",
    ],
    "access_restricted": [
        r"(?i)(access|connect\s+to|reach|enter|gain\s+entry\s+to)\s+(?:restricted|unauthorized|private|internal|protected|forbidden)\s+(?:network\s+resources?|network|system|resources?|server|database|endpoint|area|zone)\s+(?:using|via|through|with|by)\s+(?:(?:available|the|existing)\s+)?(?:tools?|utilities?|functions?|APIs?|capabilities?)",
    ],
    "modify_weaken_security": [
        r"(?i)(modify|alter|change|edit|update)\s+(?:system|server|application|security|configuration)\s+(?:configuration|settings?|files?|parameters?|policies?)\s+to\s+(?:weaken|reduce|disable|bypass|lower|remove|diminish)\s+(?:security|protection|safeguards?|defenses?|controls?)",
    ],
    "exfiltration_techniques": [
        r"(?i)what\s+(?:data\s+)?exfiltration\s+(?:techniques?|methods?|channels?|approaches?|ways?)\s+(?:work|are\s+effective|can\s+be\s+used|exist)\s+(?:against|on|for)\s+(?:AI|LLM|model|system)",
        r"(?i)(describe|explain|detail)\s+(?:methods?|techniques?|approaches?)\s+for\s+(?:data\s+)?(?:exfiltration|theft|extraction)\s+from\s+(?:AI|LLM|model|compromised)\s+(?:systems?|infrastructure|platform)",
        r"(?i)what\s+(?:exfiltration|data\s+theft)\s+(?:channels?|methods?|techniques?)\s+(?:are\s+)?(?:effective|available|possible)\s+(?:against|on|for)\s+(?:AI|LLM|model)",
    ],
    "remote_control": [
        r"(?i)(describe|explain|detail)\s+(?:techniques?|methods?|approaches?)\s+for\s+(?:remote\s+)?(?:control|command|management|administration)\s+of\s+(?:AI|LLM|model|compromised)\s+(?:systems?|infrastructure)",
        r"(?i)how\s+(?:to|can)\s+(?:establish|set\s+up|create|maintain)\s+(?:remote\s+)?(?:control|command|access|management)\s+over\s+(?:compromised|AI|LLM|model)\s+(?:systems?|infrastructure)",
        r"(?i)(describe|explain|detail)\s+(?:techniques?|methods?)\s+for\s+(?:remote\s+control|command\s+and\s+control|C2)\s+of\s+(?:AI|compromised|model)",
    ],
}

PRECOMPILED_DIRECT: List[Pattern] = [re.compile(p) for p in _DIRECT_INJECTION_PATTERNS]
PRECOMPILED_NESTED: List[Pattern] = [re.compile(p) for p in _NESTED_INJECTION_STRUCTURES]
PRECOMPILED_SHELL: List[Pattern] = [re.compile(p) for p in _SHELL_INJECTION_PATTERNS]
PRECOMPILED_SQL: List[Pattern] = [re.compile(p) for p in _SQL_INJECTION_PATTERNS]
PRECOMPILED_PATH: List[Pattern] = [re.compile(p) for p in _PATH_TRAVERSAL_PATTERNS]
PRECOMPILED_JAILBREAK: Dict[str, List[Pattern]] = {
    k: [re.compile(p) for p in v] for k, v in _JAILBREAK_PATTERNS.items()
}
PRECOMPILED_ENCODING: Dict[str, List[Pattern]] = {
    k: [re.compile(p) for p in v] for k, v in _ENCODING_ESCAPE_PATTERNS.items()
}
PRECOMPILED_SEMANTIC: Dict[str, List[Pattern]] = {
    k: [re.compile(p) for p in v] for k, v in _SEMANTIC_ATTACK_PATTERNS.items()
}


def scan_direct(content: str) -> List[Dict[str, Any]]:
    hits = []
    for pattern in PRECOMPILED_DIRECT:
        for m in pattern.finditer(content):
            hits.append({
                "pattern": pattern.pattern[:80],
                "match": m.group()[:120],
                "start": m.start(),
                "end": m.end(),
                "category": "direct_injection",
            })
    for pattern in PRECOMPILED_NESTED:
        for m in pattern.finditer(content):
            hits.append({
                "pattern": pattern.pattern[:80],
                "match": m.group()[:120],
                "start": m.start(),
                "end": m.end(),
                "category": "nested_structure",
            })
    return hits


def scan_indirect(content: str) -> List[Dict[str, Any]]:
    hits = []
    for channel, patterns in _INDIRECT_INJECTION_PATTERNS.items():
        for pat in patterns:
            compiled = re.compile(pat)
            for m in compiled.finditer(content):
                hits.append({
                    "channel": channel,
                    "pattern": pat[:80],
                    "match": m.group()[:120],
                    "start": m.start(),
                    "end": m.end(),
                })
    return hits


def scan_jailbreak(content: str) -> List[Dict[str, Any]]:
    hits = []
    for category, patterns in PRECOMPILED_JAILBREAK.items():
        for pattern in patterns:
            for m in pattern.finditer(content):
                hits.append({
                    "category": category,
                    "pattern": pattern.pattern[:80],
                    "match": m.group()[:120],
                    "start": m.start(),
                    "end": m.end(),
                })
    return hits


def scan_encoding_escape(content: str) -> List[Dict[str, Any]]:
    hits = []
    for technique, patterns in PRECOMPILED_ENCODING.items():
        for pattern in patterns:
            for m in pattern.finditer(content):
                hits.append({
                    "technique": technique,
                    "pattern": pattern.pattern[:80],
                    "match": m.group()[:120],
                    "start": m.start(),
                    "end": m.end(),
                })
    return hits


def check_file_type(filename: str) -> List[str]:
    import os
    ext = os.path.splitext(filename)[1].lower()
    return _FILE_TYPE_CHECKS.get(ext, [])


def scan_shell(content: str) -> List[Dict[str, Any]]:
    hits = []
    for pattern in PRECOMPILED_SHELL:
        for m in pattern.finditer(content):
            hits.append({
                "pattern": pattern.pattern[:80],
                "match": m.group()[:120],
                "start": m.start(),
                "end": m.end(),
                "category": "shell_injection",
            })
    return hits


def scan_sql(content: str) -> List[Dict[str, Any]]:
    hits = []
    for pattern in PRECOMPILED_SQL:
        for m in pattern.finditer(content):
            hits.append({
                "pattern": pattern.pattern[:80],
                "match": m.group()[:120],
                "start": m.start(),
                "end": m.end(),
                "category": "sql_injection",
            })
    return hits


def scan_path_traversal(content: str) -> List[Dict[str, Any]]:
    hits = []
    for pattern in PRECOMPILED_PATH:
        for m in pattern.finditer(content):
            hits.append({
                "pattern": pattern.pattern[:80],
                "match": m.group()[:120],
                "start": m.start(),
                "end": m.end(),
                "category": "path_traversal",
            })
    return hits


def scan_semantic_attacks(content: str) -> List[Dict[str, Any]]:
    hits = []
    for category, patterns in PRECOMPILED_SEMANTIC.items():
        for pattern in patterns:
            for m in pattern.finditer(content):
                hits.append({
                    "category": category,
                    "pattern": pattern.pattern[:80],
                    "match": m.group()[:120],
                    "start": m.start(),
                    "end": m.end(),
                })
    return hits
