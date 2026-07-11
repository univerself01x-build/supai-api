import type { paths } from "./api.generated";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

type ProjectListResponse = paths["/api/projects"]["get"]["responses"]["200"]["content"]["application/json"];
type ProjectDetailResponse = paths["/api/projects/{project_id}"]["get"]["responses"]["200"]["content"]["application/json"];
type MatchResponse = paths["/api/match"]["post"]["responses"]["200"]["content"]["application/json"];
type ConfirmResponse = paths["/api/projects/{project_id}/confirm"]["post"]["responses"]["200"]["content"]["application/json"];

export type ProjectCard = ProjectListResponse["human"][number];
export type ProjectDetail = ProjectDetailResponse["human"];
export type MatchResult = MatchResponse["human"];
export type TeamSlot = ProjectDetail["team"][number];

export async function fetchProjects(): Promise<ProjectCard[]> {
  const res = await fetch(`${API_BASE}/api/projects?role=fengge`);
  const data: ProjectListResponse = await res.json();
  return data.human;
}

export async function fetchProject(id: string): Promise<ProjectDetail> {
  const res = await fetch(`${API_BASE}/api/projects/${id}?role=fengge`);
  const data: ProjectDetailResponse = await res.json();
  return data.human;
}

export async function matchRequest(input: {
  scene: string;
  budget: number;
  location?: string;
  roles?: string[];
  customRoles?: string[];
}): Promise<MatchResult> {
  const res = await fetch(`${API_BASE}/api/match`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  const data: MatchResponse = await res.json();
  return data.human;
}

export async function confirmRoles(
  projectId: string,
  confirmedRoles: { role: string; photographerId: string; source: string }[]
): Promise<ConfirmResponse> {
  const res = await fetch(`${API_BASE}/api/projects/${projectId}/confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ confirmedRoles }),
  });
  return res.json();
}
