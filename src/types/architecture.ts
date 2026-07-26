export interface ArchitectureSection {
  id: string;
  title: string;
  icon: string;
  description: string;
}

export interface FolderNode {
  name: string;
  type: 'folder' | 'file';
  purpose: string;
  children?: FolderNode[];
}

export interface ContainerInfo {
  name: string;
  service: string;
  image: string;
  ports: string[];
  purpose: string;
  healthcheck: string;
  restartPolicy: string;
}

export interface RequestStep {
  stepNumber: number;
  from: string;
  to: string;
  protocol: string;
  payload: string;
  description: string;
  securityNote: string;
}

export interface EnvVar {
  name: string;
  service: string;
  required: boolean;
  sensitive: boolean;
  description: string;
  example: string;
}
