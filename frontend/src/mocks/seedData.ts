// 本地种子数据由后端 database/init.sql + backend/src/seed.py 提供，
// 前端全部通过 /api 访问本地数据库，禁止接入第三方 API。
// 本文件仅保留“本地数据来源”的占位说明与枚举默认值，供构造器/单测引用。
import { InspectionStatus } from "../constants/InspectionStatus";

export const LOCAL_DATA_NOTE = "所有数据来自本地 PostgreSQL 与后端播种脚本";

export const seedStatuses: string[] = [...InspectionStatus];
