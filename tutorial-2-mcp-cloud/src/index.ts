import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { McpAgent } from "agents/mcp";
import { z } from "zod";

interface Project{
	id: string;
	name: string;
	description: string;
	createdAt: string;
	updatedAt: string;
}

interface Todo{
	id: string;
	projectId: string;
	title: string;
	description: string;
	status: "pending" | "in-progress" | "completed";
	priority: "low" | "medium" | "high";
	createdAt: string;
	updatedAt: string;
}
// Define our MCP agent with tools
export class MyMCP extends McpAgent {
	server = new McpServer({
		name: "Project Planner MCP",
		version: "1.0.0",
	});

	private get kv(): KVNamespace{
		return (this.env as Env).PROJECT_PLANNER_STORE;
	}

	private async getProjectsList(): Promise<string[]> {
		const listData = await this.kv.get("projects_list");
		return listData ? JSON.parse(listData) : [];
	
	}

	private async getTodoList(projectId:string): Promise<string[]> {
		const listData = await this.kv.get(`project:${projectId}:todos`);
		return listData ? JSON.parse(listData) : [];
	
	}

	private async getTodosByProject(projectId:string): Promise<Todo[]> {
		const todoIds = await this.getTodoList(projectId);
		const todos: Todo[] = [];

		for (const todoId of todoIds) {
			const todoData = await this.kv.get(`todo:${todoId}`);
			if (todoData) {
				todos.push(JSON.parse(todoData));
			}
		}

		return todos;
	}

	async init() {
		this.server.tool("create_project", "Create a new project", {
			name: z.string().describe("Name of the project"),
			description: z.string().optional().describe("Description of the project"),
		}, async ({name,description}) => {
			const projectId = crypto.randomUUID();
			const project: Project = {
				id: projectId,
				name,
				description: description || "",
				createdAt: new Date().toISOString(),
				updatedAt: new Date().toISOString(),
			};

			await this.kv.put(`project:${projectId}`,
				 JSON.stringify(project));

			const projectsList = await this.getProjectsList();
			projectsList.push(projectId);
			await this.kv.put("projects_list", JSON.stringify(projectsList));

			// Here you would typically save the project to a database
			return{
				content: [
					{
						type: "text",
						text: JSON.stringify(project, null, 2)
					}
				],
			};
		});

		this.server.tool("list_projects", "List all projects", {}, async () => {
			const projectsList = await this.getProjectsList();
			const projects: Project[] = [];
			
			for (const projectId of projectsList) {
				const projectData = await this.kv.get(`project:${projectId}`);
				if (projectData) {
					projects.push(JSON.parse(projectData));
				}
			}

			return{
				content: [
					{
						type: "text",
						text: JSON.stringify(projects, null, 2)
					}
				],
			};
		});

		this.server.tool("get_project", "Get a project by ID", {projectId: z.string().describe("ID of the project")}, async ({projectId}) => {		

			const projectData = await this.kv.get(`project:${projectId}`);
			if (!projectData) {
				throw new Error(`Project with this id:${projectId} does not exist.`);
			}
			const project: Project = JSON.parse(projectData);
			const todos = await this.getTodosByProject(projectId);
			return{
				content: [
					{
						type: "text",
						text: JSON.stringify({project, todos}, null, 2)
					}
				],
			};
		});

		this.server.tool("delete_project", "Delete a project and all its todos", {projectId: z.string().describe("ID of the project")}, async ({projectId}) => {		

			const projectData = await this.kv.get(`project:${projectId}`);
			if (!projectData) {
				throw new Error(`Project with this id:${projectId} does not exist.`);
			}
			const todos = await this.getTodosByProject(projectId);
			for(const todo of todos){
				await this.kv.delete(`todo:${todo.id}`);
			}
			await this.kv.delete(`project:${projectId}:todos`);
			await this.kv.delete(`project:${projectId}`);

			const projectsList = await this.getProjectsList();

			const updatedProjectsList = projectsList.filter(id => id !== projectId);
			await this.kv.put("projects_list", JSON.stringify(updatedProjectsList));
			const project: Project = JSON.parse(projectData);

			return{
				content: [
					{
						type: "text",
						text: `Project ${project.name} and its todos have been deleted successfully.`
					}
				],
			};
		});

		this.server.tool("create_todo", "Create a new todo in a project", {
			projectId: z.string().describe("ID of the project"),
			title: z.string().describe("Title of the todo"),
			description: z.string().optional().describe("Description of the todo"),
			status: z.enum(["pending", "in-progress", "completed"]).describe("Status of the todo"),
			priority: z.enum(["low", "medium", "high"])
					   .optional()
					   .describe("Priority of the todo"),
		}, async ({projectId, title, description, status, priority}) => {
			const projectData = await this.kv.get(`project:${projectId}`);
			if (!projectData) {
				throw new Error(`Project with this id:${projectId} does not exist.`);
			}

			const todoId = crypto.randomUUID();
			const todo: Todo = {
				id: todoId,
				projectId: projectId,
				title,
				description: description || "",
				status: status,
				priority: priority || "medium",
				createdAt: new Date().toISOString(),
				updatedAt: new Date().toISOString(),
			};
			
			await this.kv.put(`todo:${todoId}`, JSON.stringify(todo));
			
			const todoList = await this.getTodoList(projectId);
			todoList.push(todoId);
			await this.kv.put(`project:${projectId}:todos`, JSON.stringify(todoList));

			// Here you would typically save the todo to a database
			return{
				content: [
					{
						type: "text",
						text: JSON.stringify(todo, null, 2)
					}
				],
			};
		});

		this.server.tool("update_todo", "Update todo in a project", {
			todoId: z.string().describe("ID of the todo"),
			title: z.string().describe("new title of the todo"),
			description: z.string().optional().describe("New description of the todo"),
			status: z.enum(["pending", "in-progress", "completed"]).describe("Status of the todo"),
			priority: z.enum(["low", "medium", "high"])
					   .optional()
					   .describe("New Priority of the todo"),
		}, async ({todoId: todoId, title, description, status, priority}) => {
			const todoData = await this.kv.get(`todo:${todoId}`);
			if (!todoData) {
				throw new Error(`Todo with this id:${todoId} does not exist.`);
			}
			const todo: Todo = JSON.parse(todoData);

			if (title !== undefined) {
				todo.title = title;
			}
			if (description !== undefined) {
				todo.description = description;
			}
			if(status !== undefined) {
				todo.status = status;
			}	
			if (priority !== undefined) {
				todo.priority = priority;
			}
			todo.updatedAt = new Date().toISOString();

			await this.kv.put(`todo:${todoId}`, JSON.stringify(todo));

			// Here you would typically update the todo in a database
			return{
				content: [
					{
						type: "text",
						text: JSON.stringify(todo, null, 2)
					}
				],
			};
		});
		this.server.tool("delete_todo", "Delete a todo from a project", {
			todoId: z.string().describe("ID of the todo"),
		}, async ({todoId}) => {
			const todoData = await this.kv.get(`todo:${todoId}`);
			if (!todoData) {
				throw new Error(`Todo with this id:${todoId} does not exist.`);
			}
			const todo: Todo = JSON.parse(todoData);
			const projectId = todo.projectId;
			
			const todoList = await this.getTodoList(projectId);
			const updatedTodoList = todoList.filter(id => id !== todoId);
			await this.kv.put(`project:${projectId}:todos`, JSON.stringify(updatedTodoList));

			await this.kv.delete(`todo:${todoId}`);

			// Here you would typically update the todo in a database
			return{
				content: [
					{
						type: "text",
						text: `Todo ${todo.title} has been deleted successfully.`
					}
				],
			};
		});
		this.server.tool("get_todo", "Get a todo by ID", {
			todoId: z.string().describe("ID of the todo"),
		}, async ({todoId}) => {
			const todoData = await this.kv.get(`todo:${todoId}`);
			if (!todoData) {
				throw new Error(`Todo with this id:${todoId} does not exist.`);
			}
			const todo: Todo = JSON.parse(todoData);

			// Here you would typically update the todo in a database
			return{
				content: [
					{
						type: "text",
						text: JSON.stringify(todo, null, 2)
					}
				],
			};
		});
		this.server.tool("list_all_todos", "Get all todos", {
			projectId: z.string().describe("Project ID to filter todos"),
			status: z.enum(["pending", "in-progress", "completed", "all"])
					   .optional()
					   .describe("Filter todos by status"),
		}, async ({projectId, status}) => {
			const projectData = await this.kv.get(`project:${projectId}`);
			if (!projectData) {
				throw new Error(`Project with this id:${projectId} does not exist.`);
			}
			let todos = await this.getTodosByProject(projectId);
			if(status && status !== "all"){
				todos = todos.filter(todo => todo.status === status);
			}

			// Here you would typically update the todo in a database
			return{
				content: [
					{
						type: "text",
						text: JSON.stringify(todos, null, 2)
					}
				],
			};
		});
	}
}

export default {
	fetch(request: Request, env: Env, ctx: ExecutionContext) {
		const url = new URL(request.url);

		if (url.pathname === "/mcp") {
			return MyMCP.serve("/mcp").fetch(request, env, ctx);
		}

		return new Response("Not found", { status: 404 });
	},
};
