import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// 1. Crear un servidor MCP
const server = new McpServer({
    name: "Tutorial 1 - Ejemplo",
    version: "1.0.0",
});

// 2. Definir las herramientas disponibles en el servidor
server.tool(
    "fetch-weather",
    "tool to fetch weather data for a given city",
    {
        city: z.string().describe("Name of the city to fetch weather for"),
    },
    async ({ city }) => {
        const response = await fetch(
            `https://geocoding-api.open-meteo.com/v1/search?name=${city}&count=10&language=en&format=json`,
        );
        const data = await response.json();

        if (data.length === 0) {
            return {
                content: [
                    {
                        type: "text",
                        text: `No se encontró información para la ciudad: ${city}`,
                    },
                ],
            };
        }

        const latitude = data.results[0].latitude;
        const longitude = data.results[0].longitude;

        const weatherResponse = await fetch(
            `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&hourly=is_day&current=temperature_2m,precipitation,rain&forecast_days=1`,
        );
        const weatherData = await weatherResponse.json();

        return {
            content: [
                {
                    type: "text",
                    text: JSON.stringify(weatherData, null, 2),
                },
            ],
        };
    },
);

// 3. Escuchar las peticiones entrantes del cliente
const transport = new StdioServerTransport();
await server.connect(transport);

