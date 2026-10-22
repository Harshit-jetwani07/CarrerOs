// Mirrors backend/app/data/seed_roles.py. Update both files together.
export type RoleDefinition = {
  name: string;
  description: string;
  skills: Record<string, number>;
};

export const ROLE_DEFINITIONS: RoleDefinition[] = [
  {
    name: "Backend Developer",
    description: "Builds and maintains server-side logic, APIs, and databases.",
    skills: { Python: 0.9, SQL: 0.9, Git: 0.7, "REST APIs": 0.9, PostgreSQL: 0.8, Docker: 0.7, Authentication: 0.6, Testing: 0.6, AWS: 0.5, Redis: 0.4 },
  },
  {
    name: "Frontend Developer",
    description: "Builds user-facing interfaces and client-side experiences.",
    skills: { JavaScript: 0.9, React: 0.9, TypeScript: 0.7, HTML: 0.6, CSS: 0.6, Git: 0.6, "REST APIs": 0.5, Testing: 0.4, "Next.js": 0.5 },
  },
  {
    name: "Full Stack Developer",
    description: "Works across both frontend and backend of an application.",
    skills: { JavaScript: 0.8, React: 0.7, Python: 0.7, SQL: 0.7, "REST APIs": 0.8, Git: 0.6, Docker: 0.5, Authentication: 0.6, PostgreSQL: 0.6, Testing: 0.5 },
  },
  {
    name: "Data Analyst",
    description: "Analyzes data to surface insights and support decisions.",
    skills: { SQL: 0.9, Python: 0.7, Excel: 0.6, Statistics: 0.7, "Data Visualization": 0.7, Pandas: 0.6 },
  },
  {
    name: "ML Engineer",
    description: "Builds and deploys machine learning models in production.",
    skills: { Python: 0.9, "Machine Learning": 0.9, SQL: 0.5, PyTorch: 0.6, Docker: 0.6, Statistics: 0.6, AWS: 0.5 },
  },
  { name: "Data Scientist", description: "Uses data, statistics and models to answer high-value questions.", skills: { Python: 0.9, SQL: 0.8, Statistics: 0.9, Pandas: 0.8, "Data Visualization": 0.7, "Machine Learning": 0.7, Excel: 0.4 } },
  { name: "DevOps Engineer", description: "Builds reliable delivery, infrastructure and observability systems.", skills: { Linux: 0.9, Docker: 0.9, Kubernetes: 0.8, AWS: 0.8, Git: 0.7, "CI/CD": 0.8, Terraform: 0.6, Python: 0.5 } },
  { name: "Cloud Engineer", description: "Designs and runs cloud infrastructure that teams can depend on.", skills: { AWS: 0.9, Linux: 0.8, Docker: 0.7, Networking: 0.8, Terraform: 0.7, Python: 0.5, Security: 0.6 } },
  { name: "Cybersecurity Analyst", description: "Protects systems by detecting, investigating and reducing risk.", skills: { Networking: 0.9, Linux: 0.8, Security: 0.9, Python: 0.6, "Incident Response": 0.8, "SIEM Tools": 0.7, "Web Security": 0.7 } },
  { name: "Mobile App Developer", description: "Builds polished applications for mobile platforms.", skills: { JavaScript: 0.7, React: 0.6, "React Native": 0.9, TypeScript: 0.7, Git: 0.6, "REST APIs": 0.7, "Mobile UI": 0.8 } },
  { name: "UI/UX Designer", description: "Researches, designs and tests intuitive product experiences.", skills: { Figma: 0.9, "User Research": 0.8, Wireframing: 0.8, Prototyping: 0.8, "Visual Design": 0.8, "Design Systems": 0.7, "Usability Testing": 0.7 } },
  { name: "Business Analyst", description: "Turns business questions into clear requirements and decisions.", skills: { Excel: 0.8, SQL: 0.7, "Data Visualization": 0.6, "Requirements Analysis": 0.9, Communication: 0.8, Statistics: 0.5 } },
  { name: "Product Manager", description: "Connects customer needs, business context and delivery decisions.", skills: { "Product Strategy": 0.9, "User Research": 0.7, Analytics: 0.7, Communication: 0.9, Wireframing: 0.5, "Requirements Analysis": 0.8 } },
];

export const ALL_SKILLS = Array.from(new Set(ROLE_DEFINITIONS.flatMap((role) => Object.keys(role.skills))));

export function priorityFor(importance: number): "HIGH" | "MEDIUM" | "LOW" {
  if (importance >= 0.7) return "HIGH";
  if (importance >= 0.4) return "MEDIUM";
  return "LOW";
}
