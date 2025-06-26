import { VoltAgent, Agent, createTool } from "@voltagent/core";
import axios from "axios";
import { z } from "zod";
import dotenv from "dotenv";

// Load environment variables
dotenv.config();

// Custom Provider for DeepSeek R1
class DeepSeekProvider {
  private endpoint = "http://localhost:11434/api/generate";
  private model = "deepseek-r1:1.5b";

  async generateText(prompt: string): Promise<string> {
    try {
      const response = await axios.post(this.endpoint, {
        model: this.model,
        prompt: prompt,
        stream: false,
        options: {
          temperature: 0.7,
          num_predict: 2048
        }
      }, {
        timeout: 60000
      });

      return response.data.response || "";
    } catch (error) {
      console.error("DeepSeek generation error:", error);
      throw new Error(`DeepSeek generation failed: ${error}`);
    }
  }
}

// Custom Provider for Gemini CLI
class GeminiCLIProvider {
  private endpoint = "http://localhost:8017";
  private model = "gemini-2.5-pro";

  async generateText(prompt: string): Promise<string> {
    try {
      const response = await axios.post(`${this.endpoint}/generate`, {
        model: this.model,
        prompt: prompt,
        max_tokens: 2048,
        temperature: 0.7,
        stream: false
      }, {
        timeout: 60000
      });

      return response.data.response || "";
    } catch (error) {
      console.error("Gemini CLI generation error:", error);
      throw new Error(`Gemini CLI generation failed: ${error}`);
    }
  }
}

// Create tools for specialized tasks
const reasoningTool = createTool({
  name: "deepseek_reasoning",
  description: "Performs step-by-step logical reasoning using DeepSeek R1",
  parameters: z.object({
    problem: z.string().describe("The problem or question to reason through"),
    context: z.string().optional().describe("Additional context for the problem")
  }),
  execute: async ({ problem, context }: { problem: string; context?: string }) => {
    const deepseek = new DeepSeekProvider();
    
    const enhancedPrompt = `
[VoltAgent Reasoning Task]
Please provide step-by-step reasoning for the following problem:

Problem: ${problem}
${context ? `Context: ${context}` : ''}

Use systematic reasoning:
1. Understand the problem
2. Break down components
3. Apply logical steps
4. Provide solution

Response:
`;

    const result = await deepseek.generateText(enhancedPrompt);
    return { reasoning: result, agent: "DeepSeek R1" };
  }
});

const researchTool = createTool({
  name: "gemini_research",
  description: "Performs comprehensive research and analysis using Gemini 2.5",
  parameters: z.object({
    topic: z.string().describe("The topic to research and analyze"),
    depth: z.enum(["basic", "comprehensive", "detailed"]).default("comprehensive").describe("Level of detail required")
  }),
  execute: async ({ topic, depth }: { topic: string; depth: "basic" | "comprehensive" | "detailed" }) => {
    const gemini = new GeminiCLIProvider();
    
    const enhancedPrompt = `
[VoltAgent Research Task]
Please provide ${depth} research and analysis on:

Topic: ${topic}

Provide well-structured, informative content appropriate for the requested depth level.

Response:
`;

    const result = await gemini.generateText(enhancedPrompt);
    return { research: result, agent: "Gemini 2.5", depth };
  }
});

const synthesisTool = createTool({
  name: "multi_agent_synthesis",
  description: "Combines insights from multiple AI agents for enhanced results",
  parameters: z.object({
    task: z.string().describe("The task requiring multiple agent perspectives"),
    agents: z.array(z.enum(["deepseek", "gemini", "both"])).default(["both"]).describe("Which agents to use")
  }),
  execute: async ({ task, agents }: { task: string; agents: string[] }) => {
    const results: any = {};
    
    // Execute with DeepSeek if requested
    if (agents.includes("deepseek") || agents.includes("both")) {
      const deepseek = new DeepSeekProvider();
      const deepseekPrompt = `[DeepSeek Analysis] ${task}`;
      results.deepseek = await deepseek.generateText(deepseekPrompt);
    }
    
    // Execute with Gemini if requested
    if (agents.includes("gemini") || agents.includes("both")) {
      const gemini = new GeminiCLIProvider();
      const geminiPrompt = `[Gemini Analysis] ${task}`;
      results.gemini = await gemini.generateText(geminiPrompt);
    }
    
    // Synthesize results if we have multiple
    if (results.deepseek && results.gemini) {
      const gemini = new GeminiCLIProvider();
      const synthesisPrompt = `
[Multi-Agent Synthesis]
Please combine and enhance these AI responses:

DeepSeek Response:
${results.deepseek}

Gemini Response:
${results.gemini}

Provide a unified, enhanced response:
`;
      results.synthesis = await gemini.generateText(synthesisPrompt);
    }
    
    return results;
  }
});

// Create specialized agents
const reasoningAgent = new Agent({
  name: "DeepSeek Reasoning Agent",
  description: "Specialized in step-by-step logical reasoning and problem solving",
  tools: [reasoningTool],
  model: null as any, // We use custom providers
});

const researchAgent = new Agent({
  name: "Gemini Research Agent", 
  description: "Specialized in comprehensive research and analysis",
  tools: [researchTool],
  model: null as any, // We use custom providers
});

const supervisorAgent = new Agent({
  name: "Multi-Agent Supervisor",
  description: "Coordinates multiple AI agents for complex tasks",
  tools: [reasoningTool, researchTool, synthesisTool],
  subAgents: [reasoningAgent, researchAgent],
  model: null as any, // We use custom providers
});

// Initialize VoltAgent
const voltAgent = new VoltAgent({
  agents: {
    reasoning: reasoningAgent,
    research: researchAgent,
    supervisor: supervisorAgent,
  },
});

// Demo function
async function runMCPVotsDemo() {
  console.log("🚀 VoltAgent Integration Demo - MCPVots Edition");
  console.log("=" .repeat(60));
  
  try {
    // Test reasoning
    console.log("\n🧠 Testing DeepSeek Reasoning Agent...");
    const reasoningResult = await reasoningTool.execute({
      problem: "If I have 15 apples and give away 1/3, then buy 8 more, how many do I have?",
      context: "Simple arithmetic word problem"
    });
    console.log("Reasoning Result:", reasoningResult.reasoning.substring(0, 200) + "...");
    
    // Test research
    console.log("\n🔍 Testing Gemini Research Agent...");
    const researchResult = await researchTool.execute({
      topic: "Latest developments in AI agent frameworks",
      depth: "comprehensive"
    });
    console.log("Research Result:", researchResult.research.substring(0, 200) + "...");
    
    // Test multi-agent synthesis
    console.log("\n🤝 Testing Multi-Agent Synthesis...");
    const synthesisResult = await synthesisTool.execute({
      task: "Explain the benefits of using multiple AI models together",
      agents: ["both"]
    });
    console.log("Synthesis Result:");
    if (synthesisResult.synthesis) {
      console.log("Combined:", synthesisResult.synthesis.substring(0, 200) + "...");
    } else {
      console.log("DeepSeek:", synthesisResult.deepseek?.substring(0, 100) + "...");
      console.log("Gemini:", synthesisResult.gemini?.substring(0, 100) + "...");
    }
    
    console.log("\n✅ VoltAgent Integration Demo Complete!");
    
  } catch (error) {
    console.error("❌ Demo failed:", error);
  }
}

// Export for use
export {
  DeepSeekProvider,
  GeminiCLIProvider,
  reasoningAgent,
  researchAgent,
  supervisorAgent,
  voltAgent,
  runMCPVotsDemo
};

// Run demo if this is the main module
if (import.meta.url === `file://${process.argv[1]}`) {
  runMCPVotsDemo();
}
