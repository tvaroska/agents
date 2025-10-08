"use client";

import { CopilotKitCSSProperties, CopilotSidebar } from "@copilotkit/react-ui";
import { useCoAgent, useCopilotAction } from "@copilotkit/react-core";
import { useState } from "react";

// State of the agent, make sure this aligns with your agent's state
type AgentState = {
  proverbs: string[];
};

// Weather card component for generative UI
function WeatherCard({ location, themeColor }: { location: string; themeColor: string }) {
  return (
    <div
      className="p-4 rounded-lg shadow-md text-white"
      style={{ backgroundColor: themeColor }}
    >
      <h3 className="text-lg font-semibold">Weather in {location}</h3>
      <p className="text-sm opacity-90">Sunny, 72°F</p>
    </div>
  );
}

function YourMainContent({ themeColor }: { themeColor: string }) {
  // 🪁 Shared State: https://docs.copilotkit.ai/coagents/shared-state
  const { state } = useCoAgent<AgentState>({
    name: "ProverbsAgent",
    initialState: {
      proverbs: [
        "CopilotKit may be new, but it's the best thing since sliced bread.",
      ],
    },
  });

  // 🪁 Generative UI: https://docs.copilotkit.ai/coagents/generative-ui
  useCopilotAction({
    name: "get_weather",
    description: "Get the weather for a given location.",
    available: "disabled",
    parameters: [
      { name: "location", type: "string", required: true },
    ],
    render: ({ args }) => {
      return <WeatherCard location={args.location} themeColor={themeColor} />;
    },
  });

  return (
    <div
      style={{ backgroundColor: themeColor }}
      className="h-screen w-screen flex justify-center items-center flex-col transition-colors duration-300"
    >
      <div className="bg-white/20 backdrop-blur-md p-8 rounded-2xl shadow-xl max-w-2xl w-full">
        <h1 className="text-4xl font-bold text-white mb-2 text-center">Proverbs</h1>
        <p className="text-gray-200 text-center italic mb-6">
          This is a demonstrative page, but it could be anything you want! 🪁
        </p>
        <hr className="border-white/20 my-6" />
        <div className="space-y-4">
          {state.proverbs.map((proverb, index) => (
            <div
              key={index}
              className="bg-white/10 backdrop-blur-sm p-4 rounded-lg border border-white/20"
            >
              <p className="text-white text-lg">{proverb}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function CopilotKitPage() {
  const [themeColor, setThemeColor] = useState("#6366f1");

  // 🪁 Frontend Tools: https://docs.copilotkit.ai/coagents/frontend-actions
  useCopilotAction({
    name: "set_theme",
    description: "Set the theme color of the web page.",
    parameters: [
      {
        name: "color",
        type: "string",
        description: "The hex color code to set as theme (e.g., #ff0000)",
        required: true,
      },
    ],
    handler: ({ color }) => {
      setThemeColor(color);
    },
  });

  return (
    <main style={{ "--copilot-kit-primary-color": themeColor } as CopilotKitCSSProperties}>
      <YourMainContent themeColor={themeColor} />
      <CopilotSidebar
        clickOutsideToClose={false}
        defaultOpen={true}
        labels={{
          title: "Popup Assistant",
          initial: `👋 Hi, there! You're chatting with an agent. This agent comes with a few tools to get you started.

For example you can try:
- Frontend Tools: "Set the theme to orange"
- Backend Tools: "Add a proverb about soap", "Remove the first proverb"
- Generative UI: "What is the weather like in San Francisco?"`,
        }}
      />
    </main>
  );
}
