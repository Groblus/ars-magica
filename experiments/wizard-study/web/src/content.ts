export type Citation = {
  source: "Ars Magica - Definitive Edition (Core Rules)";
  locator: `reviewed/Ars Magica - Definitive Edition (Core Rules).md:${string}`;
  note?: string;
};

export type RoleId = "storyguide" | "magus" | "companion" | "grog";

export type RolePrimer = {
  id: RoleId;
  name: string;
  tableJob: string;
  playFeel: string;
  goodFirstMove: string;
  watchFor: string;
  citations: Citation[];
};

export type PrimerChapter = {
  id: string;
  title: string;
  subtitle: string;
  readTimeMinutes: number;
  summary: string;
  essentials: string[];
  tablePrompts: string[];
  citations: Citation[];
};

export type AcademyStep = {
  title: string;
  body: string;
  example?: string;
  citations?: Citation[];
};

export type AcademyCheck = {
  question: string;
  options: string[];
  correctAnswer: number;
  explanation: string;
};

export type AcademyLesson = {
  id: string;
  title: string;
  focus: "dice" | "resolution" | "magic";
  playerGoal: string;
  intro: string;
  steps: AcademyStep[];
  check: AcademyCheck;
  citations: Citation[];
};

const core = (
  locator: Citation["locator"],
  note?: string,
): Citation => ({
  source: "Ars Magica - Definitive Edition (Core Rules)",
  locator,
  note,
});

export const rolePrimers: RolePrimer[] = [
  {
    id: "storyguide",
    name: "Storyguide",
    tableJob:
      "Frame scenes, play opposition and patrons, answer rules calls, and keep saga pressure moving.",
    playFeel:
      "Part referee, part director. You do not own every story; troupe play spreads authorship.",
    goodFirstMove:
      "Ask each player what their character wants this season, then put one concrete obstacle in front of it.",
    watchFor:
      "Avoid secret-lore dumps. Start with choices, visible stakes, and one strange detail.",
    citations: [
      core("reviewed/Ars Magica - Definitive Edition (Core Rules).md:370-373"),
      core("reviewed/Ars Magica - Definitive Edition (Core Rules).md:376-380"),
      core("reviewed/Ars Magica - Definitive Edition (Core Rules).md:22257-22269"),
    ],
  },
  {
    id: "magus",
    name: "Magus",
    tableJob:
      "Drive Hermetic ambition: research, covenant politics, spellcasting, apprentices, vis, and long plans.",
    playFeel:
      "Powerful but constrained. Magic solves many problems and creates political, social, and spiritual costs.",
    goodFirstMove:
      "Pick a House, one magical obsession, and one reason your covenant matters more than comfort.",
    watchFor:
      "Do not play only from power. Your best scenes often start where magic is risky, public, slow, or politically costly.",
    citations: [
      core("reviewed/Ars Magica - Definitive Edition (Core Rules).md:973-983"),
      core("reviewed/Ars Magica - Definitive Edition (Core Rules).md:2208-2216"),
      core("reviewed/Ars Magica - Definitive Edition (Core Rules).md:2262-2284"),
    ],
  },
  {
    id: "companion",
    name: "Companion",
    tableJob:
      "Bring worldly expertise, social leverage, faith, nobility, craft, crime, travel, or local ties into play.",
    playFeel:
      "Closer to ordinary society than magi, but still exceptional enough to shape whole stories.",
    goodFirstMove:
      "Name one community that trusts you, one that fears you, and one magus who needs your help.",
    watchFor:
      "Companions are not sidekicks. Give them goals that can pull magi into trouble.",
    citations: [
      core("reviewed/Ars Magica - Definitive Edition (Core Rules).md:985-992"),
      core("reviewed/Ars Magica - Definitive Edition (Core Rules).md:2221"),
      core("reviewed/Ars Magica - Definitive Edition (Core Rules).md:2297-2300"),
    ],
  },
  {
    id: "grog",
    name: "Grog",
    tableJob:
      "Handle dangerous, practical, and human-scale scenes: guards, servants, scouts, shield grogs, teamsters, and locals.",
    playFeel:
      "Fast to learn, easy to share, and perfect when main characters are absent or too important for a risky errand.",
    goodFirstMove:
      "Give each grog one sharp skill, one fear, and one loyalty inside the covenant.",
    watchFor:
      "Keep grogs vivid but light. They should enter play fast and reveal character through action.",
    citations: [
      core("reviewed/Ars Magica - Definitive Edition (Core Rules).md:1001-1009"),
      core("reviewed/Ars Magica - Definitive Edition (Core Rules).md:2210"),
      core("reviewed/Ars Magica - Definitive Edition (Core Rules).md:2295"),
    ],
  },
];

export const primerChapters: PrimerChapter[] = [
  {
    id: "mythic-europe-1220",
    title: "Mythic Europe, 1220",
    subtitle: "History as medieval people think it works",
    readTimeMinutes: 3,
    summary:
      "Ars Magica starts from Europe in 1220, then treats folklore, faith, demons, faeries, saints, scholars, and magic as active forces. Use real geography and medieval assumptions as texture, not homework.",
    essentials: [
      "Begin with familiar Europe: villages, roads, monasteries, courts, forests, wars, and trade.",
      "Add mythic truth: old stories matter, invisible powers bargain, and wonder can be local.",
      "Keep first scenes concrete: one place, one problem, one reason characters cannot ignore it.",
    ],
    tablePrompts: [
      "Which local belief is true in your covenant's valley?",
      "Who benefits if outsiders never understand this place?",
    ],
    citations: [
      core("reviewed/Ars Magica - Definitive Edition (Core Rules).md:360-365"),
    ],
  },
  {
    id: "troupe-play",
    title: "Troupe Play",
    subtitle: "Shared cast, shared saga, rotating spotlight",
    readTimeMinutes: 4,
    summary:
      "A saga is not one hero plus helpers. Players may portray magi, companions, and grogs at different times, while Storyguide duties and story ownership can move around the table.",
    essentials: [
      "Choose the right character for the scene instead of forcing one protagonist into every problem.",
      "Let magi anchor long-term magical ambition while companions and grogs make the world playable.",
      "Talk openly about spotlight, absent characters, and who frames the next story.",
    ],
    tablePrompts: [
      "Which scenes belong to magi, and which get better when magi stay home?",
      "Who at the table wants to try Storyguiding a small problem first?",
    ],
    citations: [
      core("reviewed/Ars Magica - Definitive Edition (Core Rules).md:370-373"),
      core("reviewed/Ars Magica - Definitive Edition (Core Rules).md:376-380"),
      core("reviewed/Ars Magica - Definitive Edition (Core Rules).md:973-1009"),
      core("reviewed/Ars Magica - Definitive Edition (Core Rules).md:22257-22269"),
    ],
  },
  {
    id: "covenant",
    title: "Covenant",
    subtitle: "Home base, laboratory, employer, political problem",
    readTimeMinutes: 4,
    summary:
      "The covenant is the saga's shared institution. It houses magi and their laboratories, but it also needs food, labor, money, guards, books, allies, secrecy, and decisions.",
    essentials: [
      "Treat the covenant as a character with needs, enemies, debts, and habits.",
      "Give players visible resources to care about: books, vis, laboratories, reputation, specialists, and safe roads.",
      "Use covenant problems to connect magical stories with mundane consequences.",
    ],
    tablePrompts: [
      "What does the covenant desperately need before winter?",
      "Which nearby power thinks the covenant owes it obedience?",
    ],
    citations: [
      core("reviewed/Ars Magica - Definitive Edition (Core Rules).md:779-787"),
    ],
  },
  {
    id: "order-and-houses",
    title: "Order and Houses",
    subtitle: "Hermetic society without a lore wall",
    readTimeMinutes: 5,
    summary:
      "The Order of Hermes gives magi a society, law, rivals, teachers, and political identity. Houses are the easiest first handle: each House points toward a style of magic, duty, or conflict.",
    essentials: [
      "For a first magus, pick House as table-facing identity, not as trivia test.",
      "Ask what your House expects from you and what you resent about that expectation.",
      "Use Hermetic society as pressure: reputation, favors, law, apprentices, and Tribunal politics.",
    ],
    tablePrompts: [
      "Which House expectation will cause trouble in session one?",
      "Which Hermetic custom does your character misunderstand or exploit?",
    ],
    citations: [
      core("reviewed/Ars Magica - Definitive Edition (Core Rules).md:635-641"),
      core("reviewed/Ars Magica - Definitive Edition (Core Rules).md:2262-2284"),
    ],
  },
  {
    id: "seasons",
    title: "Seasons",
    subtitle: "Adventure time and laboratory time both matter",
    readTimeMinutes: 3,
    summary:
      "Ars Magica cares about years. Adventures create pressure and consequences; seasons let characters study, invent, copy, train, recover, and invest in the covenant.",
    essentials: [
      "Ask what each important character does this season.",
      "Let downtime choices create future adventures: books sought, vis spent, favors owed, apprentices noticed.",
      "Use seasonal rhythm to make long plans feel playable rather than abstract.",
    ],
    tablePrompts: [
      "What would your character spend a peaceful season improving?",
      "What event ruins that peaceful season?",
    ],
    citations: [
      core("reviewed/Ars Magica - Definitive Edition (Core Rules).md:15944-15946"),
      core("reviewed/Ars Magica - Definitive Edition (Core Rules).md:16005-16009"),
    ],
  },
  {
    id: "first-session",
    title: "First-Session Expectations",
    subtitle: "Small start, clear roles, playable mystery",
    readTimeMinutes: 4,
    summary:
      "A strong first session teaches by doing. Start with a covenant problem, assign table roles plainly, introduce one Hermetic fact, and make sure every player can act before they understand the whole setting.",
    essentials: [
      "Use starter or guided characters if full creation would slow the table.",
      "Give each player a reason to care about the covenant today.",
      "Explain rules at point of use: die roll first, action total next, magic when someone casts.",
      "End with one seasonal decision so players feel the saga scale.",
    ],
    tablePrompts: [
      "Who is missing, dead, sick, angry, or owed payment when play begins?",
      "Which non-magus gets the first decisive scene?",
    ],
    citations: [
      core("reviewed/Ars Magica - Definitive Edition (Core Rules).md:2224"),
      core("reviewed/Ars Magica - Definitive Edition (Core Rules).md:2205-2222"),
      core("reviewed/Ars Magica - Definitive Edition (Core Rules).md:468-500"),
    ],
  },
];

export const academyLessons: AcademyLesson[] = [
  {
    id: "simple-and-stress-dice",
    title: "Simple Dice and Stress Dice",
    focus: "dice",
    playerGoal:
      "Know which d10 roll to use when situation is calm, risky, or story-critical.",
    intro:
      "Most rolls start with a ten-sided die. Key choice is not math; it is whether failure and weird fortune matter enough for stress.",
    steps: [
      {
        title: "Use simple die for ordinary uncertainty",
        body:
          "When action has uncertainty but no exceptional danger or dramatic pressure, roll one d10 and read the number directly.",
        example:
          "A calm search through stored covenant supplies can use a simple die.",
      },
      {
        title: "Use stress die when danger or drama can bite",
        body:
          "When outcome matters under pressure, use stress die. High fortune can explode upward; bad fortune can open botch risk when circumstances are dangerous.",
        example:
          "Casting in combat, climbing during a storm, or lying to a suspicious noble calls for stress.",
      },
      {
        title: "Botch risk belongs to meaningful trouble",
        body:
          "Botches are not punishment for rolling. They mark situations where something can go unusually wrong and story should respond.",
      },
    ],
    check: {
      question:
        "A grog crosses a rotten bridge while wolves close behind. Which die should table reach for?",
      options: [
        "Simple die, because crossing a bridge is ordinary movement.",
        "Stress die, because danger and pressure make extreme outcomes matter.",
        "No die, because grogs do not use core resolution.",
      ],
      correctAnswer: 1,
      explanation:
        "Rotten bridge plus wolves makes outcome dangerous and dramatic. Stress die fits.",
    },
    citations: [
      core("reviewed/Ars Magica - Definitive Edition (Core Rules).md:468-500"),
    ],
  },
  {
    id: "action-totals",
    title: "Action Totals",
    focus: "resolution",
    playerGoal:
      "Read most non-magic rolls as die plus relevant trait plus relevant Ability plus modifiers.",
    intro:
      "Ars Magica resolution usually asks one plain question: what total did character bring to this specific action?",
    steps: [
      {
        title: "Name exact action first",
        body:
          "Before numbers, state what character tries to do and what success changes in scene.",
        example:
          "Not 'I use Charm,' but 'I calm the miller enough that he lets us inspect the cellar.'",
      },
      {
        title: "Build total from die, trait, Ability, modifiers",
        body:
          "Pick relevant Characteristic and Ability, add die result, then add or subtract situational modifiers.",
        example:
          "Presence plus Charm plus die can fit social reassurance; Dexterity plus Athletics plus die can fit a leap.",
      },
      {
        title: "Compare against target",
        body:
          "Storyguide compares total with an Ease Factor, opponent total, or other stated target. Margin helps describe quality.",
      },
    ],
    check: {
      question:
        "Player says, 'I convince the reeve to let us search the barn.' What should table do first?",
      options: [
        "Pick any high Ability and roll immediately.",
        "State action and stakes, then choose fitting Characteristic and Ability.",
        "Use Hermetic casting total because persuasion is social magic.",
      ],
      correctAnswer: 1,
      explanation:
        "Action total starts from clear fictional action, then uses fitting numbers.",
    },
    citations: [
      core("reviewed/Ars Magica - Definitive Edition (Core Rules).md:468-470"),
    ],
  },
  {
    id: "hermetic-casting-and-penetration",
    title: "Hermetic Casting and Penetration",
    focus: "magic",
    playerGoal:
      "Choose correct Formulaic die, understand casting total and spell level, then check whether magic penetrates resistance.",
    intro:
      "Hermetic magic has two gates. First, can magus cast spell well enough? Second, if target has Magic Resistance, does spell penetrate it?",
    steps: [
      {
        title: "Match spell to Technique and Form",
        body:
          "Hermetic spells combine what magic does with what it affects. Casting uses relevant Technique and Form Arts.",
        example:
          "A fire-creating spell points to Creo and Ignem.",
      },
      {
        title: "Build casting total",
        body:
          "Casting total uses relevant Arts, Stamina, aura, die, and other modifiers. Compare result with spell level to see how cleanly spell works.",
      },
      {
        title: "Choose die from situation",
        body:
          "Use a simple die when casting is calm. Under pressure use a stress die, including its explosion and possible botch check. Mastered magic can change that choice in specific cases; this lesson does not model mastery.",
        example:
          "Try Calm with raw face 0, then Pressure with sequence 1,5. Enter every stress and botch face yourself.",
      },
      {
        title: "Check penetration against resistance",
        body:
          "If magic must affect something protected by Magic Resistance, casting success is not enough. Penetration must exceed that resistance for spell to take hold.",
        example:
          "A spell can be cast correctly and still fail to affect a warded creature.",
      },
    ],
    check: {
      question:
        "A magus successfully casts a spell at a creature with Magic Resistance, but final Penetration is too low. What happens?",
      options: [
        "Spell is cast, but it does not affect protected target.",
        "Spell automatically botches.",
        "Creature takes half effect.",
      ],
      correctAnswer: 0,
      explanation:
        "Casting and penetration are separate gates. Low penetration means protected target resists effect.",
    },
    citations: [
      core("reviewed/Ars Magica - Definitive Edition (Core Rules).md:9085-9115"),
      core("reviewed/Ars Magica - Definitive Edition (Core Rules).md:9153-9165"),
    ],
  },
];

export const newPlayerPrimer = {
  title: "Start Here: Ars Magica Definitive Edition",
  audience: "new players, Storyguides, and software features that need spoiler-safe onboarding",
  chapters: primerChapters,
  roles: rolePrimers,
} as const;
