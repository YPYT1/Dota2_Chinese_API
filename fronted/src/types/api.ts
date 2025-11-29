// Lua API Types
export interface LuaParameter {
  name: string;
  type: string;
  typeLink: string | null;
  isOptional: boolean;
  description: string | null;
  description_cn: string;
  type_description_cn: string;
}

export interface OptionField {
  name: string;
  type: string;
  typeLink: string | null;
  isOptional: boolean;
  description_cn: string;
  type_description_cn: string;
}

export interface OptionObject {
  name: string;
  extends: string | null;
  fields: OptionField[];
}

export interface LuaMethod {
  name: string;
  signature: string;
  description: string | null;
  server: boolean;
  client: boolean;
  githubLink: string;
  googleLink: string;
  link: string;
  parameters: LuaParameter[];
  returnType: string;
  returnTypeLink: string | null;
  name_cn: string;
  description_cn: string;
  returnType_cn: string;
  returnDescription_cn: string;
  example_ts: string;
  notes_cn: string;
  warnings_cn: string;
  common_usage_cn: string;
  related: string[];
  tags: string[];
  deprecated: boolean;
  options?: OptionObject[];
}

export interface LuaClass {
  name: string;
  extends: string | null;
  extendsLink: string | null;
  description: string | null;
  references: number;
  server: boolean;
  client: boolean;
  link: string;
  name_cn: string;
  description_cn: string;
  notes_cn: string;
  warnings_cn: string;
  example_ts: string;
  common_usage_cn: string;
  related: string[];
  see_also: string[];
  tags: string[];
  deprecated: boolean;
  since_version: string;
  fields: unknown[];
  methods: LuaMethod[];
}

export interface LuaFunction {
  name: string;
  signature: string;
  description: string | null;
  server: boolean;
  client: boolean;
  githubLink: string;
  googleLink: string;
  link: string;
  parameters: LuaParameter[];
  returnType: string;
  returnTypeLink: string | null;
  name_cn: string;
  description_cn: string;
  returnType_cn: string;
  returnDescription_cn: string;
  example_ts: string;
  notes_cn: string;
  warnings_cn: string;
  common_usage_cn: string;
  related: string[];
  tags: string[];
  deprecated: boolean;
  see_also: string[];
}

export interface LuaEnumMember {
  name: string;
  value: number;
  description: string | null;
  description_cn: string;
}

export interface LuaEnum {
  name: string;
  description: string | null;
  references: number;
  link: string;
  members: LuaEnumMember[];
  name_cn: string;
  description_cn: string;
  example_ts: string;
  notes_cn: string;
  common_usage_cn: string;
  related: string[];
  see_also: string[];
  tags: string[];
  warnings_cn: string;
}

export interface LuaConstant {
  name: string;
  value: number;
  valueType: string;
  link: string;
  name_cn: string;
  description_cn: string;
  example_ts: string;
  notes_cn: string;
  common_usage_cn: string;
  related: string[];
  see_also: string[];
  tags: string[];
}

// Game Events Types
export interface EventParameter {
  name: string;
  type: string;
  description: string | null;
  description_cn: string;
  type_description_cn: string;
}

export interface GameEvent {
  name: string;
  signature: string;
  description: string | null;
  parameters: EventParameter[];
  returnType: string;
  isRecommended: boolean;
  githubLink: string;
  googleLink: string;
  link: string;
  name_cn: string;
  description_cn: string;
  example_ts: string;
  notes_cn: string;
  common_usage_cn: string;
  related: string[];
  see_also: string[];
  tags: string[];
}

// Panorama Types
export interface PanoramaEnumMember {
  name: string;
  value: number;
  description: string | null;
  methodName: string | null;
  description_cn: string;
  methodName_cn: string;
}

export interface PanoramaEnum {
  name: string;
  referencesLink: string;
  link: string;
  members: PanoramaEnumMember[];
  name_cn: string;
  description_cn: string;
  usage_cn: string;
  example_ts: string;
  notes_cn: string;
  related: string[];
  see_also: string[];
  tags: string[];
}

export interface PanoramaEventParameter {
  name: string;
  type: string;
  description_cn: string;
  type_description_cn: string;
}

export interface PanoramaEvent {
  name: string;
  signature: string;
  description: string;
  parameters: PanoramaEventParameter[];
  returnType: string;
  githubLink: string;
  googleLink: string;
  link: string;
  name_cn: string;
  description_cn: string;
  example_ts: string;
  notes_cn: string;
  usage_cn: string;
  related: string[];
  see_also: string[];
  tags: string[];
}

// Metadata Types
export interface Metadata {
  type: string;
  source: string;
  crawledAt: string;
  count: number;
  translated_at?: string;
  model?: string;
  recommendedCount?: number;
}

export interface DataFile<T> {
  metadata: Metadata;
  items: T[];
}

// Navigation Types
export interface NavItem {
  name: string;
  href: string;
  icon?: string;
}

export type ApiCategory = 'classes' | 'functions' | 'constants' | 'enums';
