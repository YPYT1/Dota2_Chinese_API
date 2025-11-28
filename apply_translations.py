#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""应用手动翻译到 CDOTA_BaseNPC 类"""

import json

# CDOTA_BaseNPC 方法翻译字典 - 第一批 (D-G开头的方法)
TRANSLATIONS = {
    "DropItemAtPositionImmediate": ("立即丢弃物品到位置", "立即将携带的物品丢弃到指定位置"),
    "EjectItemFromStash": ("从储藏处弹出物品", "将物品从储藏处弹出"),
    "FaceTowards": ("面向目标", "使单位面向指定位置"),
    "FadeGesture": ("淡出动作", "淡出指定的动作"),
    "FindAbilityByName": ("通过名称查找技能", "通过名称查找单位拥有的技能"),
    "FindAllModifiers": ("查找所有修饰器", "获取单位身上的所有修饰器"),
    "FindAllModifiersByName": ("通过名称查找所有修饰器", "通过名称查找单位身上的所有同名修饰器"),
    "FindItemInInventory": ("在物品栏中查找物品", "在单位的物品栏中查找指定物品"),
    "FindModifierByName": ("通过名称查找修饰器", "通过名称查找单位身上的修饰器"),
    "FindModifierByNameAndCaster": ("通过名称和施法者查找修饰器", "通过修饰器名称和施法者查找修饰器"),
    "ForceKill": ("强制击杀", "强制击杀该单位"),
    "ForcePlayActivityOnce": ("强制播放动作一次", "强制单位播放一次指定动作"),
    "GetAbilityByIndex": ("通过索引获取技能", "通过索引获取单位的技能"),
    "GetAbilityCount": ("获取技能数量", "获取单位拥有的技能数量"),
    "GetAcquisitionRange": ("获取索敌范围", "获取单位的自动索敌范围"),
    "GetAdditionalBattleMusicWeight": ("获取额外战斗音乐权重", "获取单位的额外战斗音乐权重值"),
    "GetAggroTarget": ("获取仇恨目标", "获取单位当前的仇恨目标"),
    "GetAttackAnimationPoint": ("获取攻击动画点", "获取攻击动画的关键点时间"),
    "GetAttackCapability": ("获取攻击能力", "获取单位的攻击能力类型"),
    "GetAttackDamage": ("获取攻击伤害", "获取单位的攻击伤害值"),
    "GetAttackRangeBuffer": ("获取攻击距离缓冲", "获取单位的攻击距离缓冲值"),
    "GetAttackSpeed": ("获取攻击速度", "获取单位的攻击速度"),
    "GetAttacksPerSecond": ("获取每秒攻击次数", "获取单位每秒的攻击次数"),
    "GetAttackTarget": ("获取攻击目标", "获取单位当前的攻击目标"),
    "GetAverageTrueAttackDamage": ("获取平均真实攻击伤害", "获取单位的平均真实攻击伤害"),
    "GetBaseAttackRange": ("获取基础攻击距离", "获取单位的基础攻击距离"),
    "GetBaseAttackTime": ("获取基础攻击间隔", "获取单位的基础攻击间隔时间"),
    "GetBaseDamageMax": ("获取基础最大伤害", "获取单位的基础最大攻击伤害"),
    "GetBaseDamageMin": ("获取基础最小伤害", "获取单位的基础最小攻击伤害"),
    "GetBaseDayTimeVisionRange": ("获取基础白天视野", "获取单位的基础白天视野范围"),
    "GetBaseHealthBarOffset": ("获取基础血条偏移", "获取单位血条的基础垂直偏移量"),
    "GetBaseHealthRegen": ("获取基础生命恢复", "获取单位的基础生命恢复速度"),
    "GetBaseMagicalResistanceValue": ("获取基础魔法抗性", "获取单位的基础魔法抗性值"),
    "GetBaseMaxHealth": ("获取基础最大生命值", "获取单位的基础最大生命值"),
    "GetBaseMoveSpeed": ("获取基础移动速度", "获取单位的基础移动速度"),
    "GetBaseNightTimeVisionRange": ("获取基础夜间视野", "获取单位的基础夜间视野范围"),
    "GetBonusManaRegen": ("获取额外法力恢复", "获取单位的额外法力恢复速度"),
    "GetCastPoint": ("获取施法前摇", "获取单位当前技能的施法前摇时间"),
    "GetCastRangeBonus": ("获取施法距离加成", "获取单位的施法距离加成值"),
    "GetCloneSource": ("获取克隆源", "如果单位是克隆体，获取其源单位"),
    "GetCollisionPadding": ("获取碰撞边距", "获取单位的碰撞边距值"),
    "GetCooldownReduction": ("获取冷却缩减", "获取单位的技能冷却缩减百分比"),
    "GetCreationTime": ("获取创建时间", "获取单位的创建时间"),
    "GetCurrentActiveAbility": ("获取当前激活技能", "获取单位当前正在使用的技能"),
    "GetCurrentVisionRange": ("获取当前视野范围", "获取单位当前的视野范围"),
    "GetCursorCastTarget": ("获取光标施法目标", "获取光标指向的施法目标"),
    "GetCursorPosition": ("获取光标位置", "获取光标的当前位置"),
    "GetCursorTargetingNothing": ("获取光标无目标状态", "检查光标是否没有选中任何目标"),
    "GetDamageMax": ("获取最大伤害", "获取单位的最大攻击伤害"),
    "GetDamageMin": ("获取最小伤害", "获取单位的最小攻击伤害"),
    "GetDayTimeVisionRange": ("获取白天视野范围", "获取单位的白天视野范围"),
    "GetDeathXP": ("获取死亡经验", "获取击杀该单位获得的经验值"),
    "GetDisplayAttackSpeed": ("获取显示攻击速度", "获取UI显示的攻击速度值"),
    "GetEvasion": ("获取闪避", "获取单位的闪避率"),
    "GetForceAttackTarget": ("获取强制攻击目标", "获取单位的强制攻击目标"),
    "GetGoldBounty": ("获取金钱奖励", "获取击杀该单位获得的金钱奖励"),
    "GetHasteFactor": ("获取加速因子", "获取单位的加速因子"),
    "GetHealth": ("获取当前生命值", "获取单位的当前生命值"),
    "GetHealthDeficit": ("获取生命值缺失", "获取单位缺失的生命值"),
    "GetHealthPercent": ("获取生命值百分比", "获取单位当前生命值百分比"),
    "GetHealthRegen": ("获取生命恢复", "获取单位的生命恢复速度"),
    "GetHullRadius": ("获取碰撞半径", "获取单位的碰撞体积半径"),
    "GetIdealSpeed": ("获取理想速度", "获取单位的理想移动速度"),
    "GetIdealSpeedNoSlows": ("获取无减速理想速度", "获取单位不受减速影响时的理想速度"),
    "GetIncreasedAttackSpeed": ("获取增加的攻击速度", "获取单位增加的攻击速度值"),
    "GetInitialGoalEntity": ("获取初始目标实体", "获取单位的初始目标实体"),
    "GetItemInSlot": ("获取槽位物品", "获取指定槽位的物品"),
    "GetLastAttackTime": ("获取上次攻击时间", "获取单位上次攻击的时间"),
    "GetLastDamageTime": ("获取上次受伤时间", "获取单位上次受到伤害的时间"),
    "GetLastIdleChangeTime": ("获取上次空闲改变时间", "获取单位上次空闲状态改变的时间"),
    "GetLevel": ("获取等级", "获取单位的当前等级"),
    "GetLifetimeKills": ("获取累计击杀数", "获取单位在本局游戏中的累计击杀数"),
    "GetMagicalArmorValue": ("获取魔法护甲值", "获取单位的魔法护甲值"),
    "GetMainControllingPlayer": ("获取主控玩家", "获取主要控制该单位的玩家"),
    "GetMana": ("获取当前法力值", "获取单位的当前法力值"),
    "GetManaPercent": ("获取法力值百分比", "获取单位当前法力值百分比"),
    "GetManaRegen": ("获取法力恢复", "获取单位的法力恢复速度"),
    "GetMaxHealth": ("获取最大生命值", "获取单位的最大生命值"),
    "GetMaxMana": ("获取最大法力值", "获取单位的最大法力值"),
    "GetMaximumGoldBounty": ("获取最大金钱奖励", "获取击杀该单位可能获得的最大金钱"),
    "GetMinimumGoldBounty": ("获取最小金钱奖励", "获取击杀该单位可能获得的最小金钱"),
    "GetModelRadius": ("获取模型半径", "获取单位模型的半径"),
    "GetModifierCount": ("获取修饰器数量", "获取单位身上的修饰器数量"),
    "GetModifierStackCount": ("获取修饰器层数", "获取指定修饰器的层数"),
    "GetMoveSpeedModifier": ("获取移速修正", "获取单位的移动速度修正值"),
    "GetNightTimeVisionRange": ("获取夜间视野范围", "获取单位的夜间视野范围"),
    "GetOpposingTeamNumber": ("获取敌对队伍编号", "获取与该单位敌对的队伍编号"),
    "GetPaddedCollisionRadius": ("获取带边距碰撞半径", "获取包含边距的碰撞半径"),
    "GetPhysicalArmorBaseValue": ("获取基础物理护甲", "获取单位的基础物理护甲值"),
    "GetPhysicalArmorValue": ("获取物理护甲值", "获取单位的物理护甲值"),
    "GetPlayerOwner": ("获取玩家所有者", "获取拥有该单位的玩家"),
    "GetPlayerOwnerID": ("获取玩家所有者ID", "获取拥有该单位的玩家ID"),
    "GetProjectileSpeed": ("获取弹道速度", "获取单位的弹道速度"),
    "GetRangeToUnit": ("获取到单位的距离", "获取到指定单位的距离"),
    "GetRemainingPathLength": ("获取剩余路径长度", "获取单位剩余移动路径的长度"),
    "GetSecondsPerAttack": ("获取每次攻击秒数", "获取单位每次攻击需要的秒数"),
    "GetSpellAmplification": ("获取技能增强", "获取单位的技能增强百分比"),
    "GetStatusResistance": ("获取状态抗性", "获取单位的状态抗性百分比"),
    "GetStrength": ("获取力量", "获取单位的力量属性值"),
    "GetTauntTarget": ("获取嘲讽目标", "获取嘲讽该单位的目标"),
    "GetTeamNumber": ("获取队伍编号", "获取单位所属的队伍编号"),
    "GetTotalPurchasedUpgradeGoldCost": ("获取升级总花费", "获取单位技能升级的总金钱花费"),
    "GetUnitLabel": ("获取单位标签", "获取单位的标签字符串"),
    "GetUnitName": ("获取单位名称", "获取单位的内部名称"),
    "GiveMana": ("给予法力值", "给予单位指定数量的法力值"),
}

# 第二批 (H开头的方法)
TRANSLATIONS.update({
    "HasAbility": ("是否拥有技能", "检查单位是否拥有指定技能"),
    "HasAnyActiveAbilities": ("是否有激活技能", "检查单位是否有任何激活的技能"),
    "HasAttackCapability": ("是否有攻击能力", "检查单位是否具有攻击能力"),
    "HasFlyingVision": ("是否有飞行视野", "检查单位是否拥有飞行视野"),
    "HasFlyMovementCapability": ("是否能飞行移动", "检查单位是否具有飞行移动能力"),
    "HasGroundMovementCapability": ("是否能地面移动", "检查单位是否具有地面移动能力"),
    "HasInventory": ("是否有物品栏", "检查单位是否拥有物品栏"),
    "HasItemInInventory": ("是否有物品", "检查单位物品栏中是否有指定物品"),
    "HasModifier": ("是否有修饰器", "检查单位是否有指定名称的修饰器"),
    "HasMovementCapability": ("是否能移动", "检查单位是否具有移动能力"),
    "HasScepter": ("是否有神杖", "检查单位是否拥有阿哈利姆神杖效果"),
    "Heal": ("治疗", "治疗单位指定数量的生命值"),
    "Hold": ("原地待命", "使单位原地待命"),
})

# 第三批 (I开头的方法)
TRANSLATIONS.update({
    "Interrupt": ("打断", "打断单位当前的动作"),
    "InterruptChannel": ("打断持续施法", "打断单位的持续施法"),
    "InterruptMotionControllers": ("打断运动控制器", "打断所有影响单位的运动控制器"),
    "IsAncient": ("是否是远古单位", "检查单位是否为远古类型"),
    "IsAttackImmune": ("是否攻击免疫", "检查单位是否免疫攻击"),
    "IsAttacking": ("是否正在攻击", "检查单位是否正在进行攻击"),
    "IsAttackingEntity": ("是否正在攻击实体", "检查单位是否正在攻击指定实体"),
    "IsBarracks": ("是否是兵营", "检查单位是否为兵营"),
    "IsBlind": ("是否致盲", "检查单位是否处于致盲状态"),
    "IsBlockDisabled": ("是否禁用格挡", "检查单位的伤害格挡是否被禁用"),
    "IsBoss": ("是否是Boss", "检查单位是否为Boss单位"),
    "IsBuilding": ("是否是建筑", "检查单位是否为建筑"),
    "IsChanneling": ("是否正在持续施法", "检查单位是否正在持续施法"),
    "IsClone": ("是否是克隆体", "检查单位是否为克隆体"),
    "IsCommandRestricted": ("是否命令受限", "检查单位是否命令受限"),
    "IsConsideredHero": ("是否视为英雄", "检查单位是否被视为英雄"),
    "IsControllableByAnyPlayer": ("是否可被任意玩家控制", "检查单位是否可被任意玩家控制"),
    "IsCourier": ("是否是信使", "检查单位是否为信使"),
    "IsCreature": ("是否是生物", "检查单位是否为生物类型"),
    "IsCreep": ("是否是小兵", "检查单位是否为小兵"),
    "IsDeniable": ("是否可反补", "检查单位是否可以被反补"),
    "IsDisarmed": ("是否被缴械", "检查单位是否处于缴械状态"),
    "IsDominated": ("是否被支配", "检查单位是否被支配"),
    "IsEvadeDisabled": ("是否闪避被禁用", "检查单位的闪避是否被禁用"),
    "IsFort": ("是否是要塞", "检查单位是否为要塞"),
    "IsFrozen": ("是否被冻结", "检查单位是否处于冻结状态"),
    "IsHero": ("是否是英雄", "检查单位是否为英雄"),
    "IsHexed": ("是否被妖术", "检查单位是否处于妖术状态"),
    "IsIdle": ("是否空闲", "检查单位是否处于空闲状态"),
    "IsIllusion": ("是否是幻象", "检查单位是否为幻象"),
    "IsInRangeOfShop": ("是否在商店范围内", "检查单位是否在商店范围内"),
    "IsInvisible": ("是否隐身", "检查单位是否处于隐身状态"),
    "IsInvulnerable": ("是否无敌", "检查单位是否处于无敌状态"),
    "IsLowAttackPriority": ("是否低攻击优先级", "检查单位是否为低攻击优先级"),
    "IsMagicImmune": ("是否魔法免疫", "检查单位是否处于魔法免疫状态"),
    "IsMoving": ("是否正在移动", "检查单位是否正在移动"),
    "IsMuted": ("是否被物品沉默", "检查单位是否被物品沉默"),
    "IsNeutralUnitType": ("是否是中立单位", "检查单位是否为中立单位类型"),
    "IsNightmared": ("是否处于噩梦", "检查单位是否处于噩梦状态"),
    "IsOpposingTeam": ("是否是敌对队伍", "检查指定队伍是否与该单位敌对"),
    "IsOther": ("是否是其他类型", "检查单位是否为其他类型"),
    "IsOutOfGame": ("是否在游戏外", "检查单位是否处于游戏外状态"),
    "IsOwnedByAnyPlayer": ("是否被玩家拥有", "检查单位是否被任何玩家拥有"),
    "IsPassivesDisabled": ("是否被动被禁用", "检查单位的被动技能是否被禁用"),
    "IsPhantom": ("是否是幻影", "检查单位是否为幻影单位"),
    "IsPhantomBlocker": ("是否是幻影阻挡者", "检查单位是否会阻挡幻影"),
    "IsPhased": ("是否相位状态", "检查单位是否处于相位状态"),
    "IsPositionInRange": ("位置是否在范围内", "检查指定位置是否在单位范围内"),
    "IsRangedAttacker": ("是否是远程攻击者", "检查单位是否为远程攻击者"),
    "IsRealHero": ("是否是真实英雄", "检查单位是否为真实英雄"),
    "IsRooted": ("是否被缠绕", "检查单位是否处于缠绕状态"),
    "IsSilenced": ("是否被沉默", "检查单位是否处于沉默状态"),
    "IsSpeciallyDeniable": ("是否可特殊反补", "检查单位是否可以被特殊反补"),
    "IsSpeciallyUndeniable": ("是否不可特殊反补", "检查单位是否不可被特殊反补"),
    "IsStrongIllusion": ("是否是强力幻象", "检查单位是否为强力幻象"),
    "IsStunned": ("是否被眩晕", "检查单位是否处于眩晕状态"),
    "IsSummoned": ("是否是召唤物", "检查单位是否为召唤物"),
    "IsTaunted": ("是否被嘲讽", "检查单位是否处于嘲讽状态"),
    "IsTempestDouble": ("是否是风暴双雄", "检查单位是否为风暴双雄"),
    "IsTower": ("是否是防御塔", "检查单位是否为防御塔"),
    "IsUnableToMiss": ("是否无法落空", "检查单位的攻击是否无法落空"),
    "IsUnselectable": ("是否不可选中", "检查单位是否不可被选中"),
    "IsUntargetable": ("是否不可作为目标", "检查单位是否不可作为技能目标"),
    "IsWard": ("是否是守卫", "检查单位是否为守卫"),
    "IsZombie": ("是否是僵尸", "检查单位是否为僵尸单位"),
})

# 第四批 (K-N开头的方法)
TRANSLATIONS.update({
    "Kill": ("击杀", "击杀该单位"),
    "MakeIllusion": ("创建幻象", "从该单位创建一个幻象"),
    "MakePhantomBlocker": ("设为幻影阻挡者", "将单位设为幻影阻挡者"),
    "MakeVisibleDueToAttack": ("因攻击而显形", "使单位因为攻击而显形"),
    "MakeVisibleToTeam": ("对队伍可见", "使单位对指定队伍可见"),
    "ManageModelChanges": ("管理模型变化", "管理单位的模型变化"),
    "ModifyHealth": ("修改生命值", "修改单位的当前生命值"),
    "MoveToNPC": ("移动到单位", "使单位移动到目标单位位置"),
    "MoveToNPCToGiveItem": ("移动到单位给予物品", "移动到目标单位位置并给予物品"),
    "MoveToPosition": ("移动到位置", "使单位移动到指定位置"),
    "MoveToPositionAggressive": ("攻击移动到位置", "使单位攻击移动到指定位置"),
    "MoveToTargetToAttack": ("移动到目标攻击", "使单位移动到目标并攻击"),
    "NoHealthBar": ("隐藏血条", "隐藏单位的血条"),
    "NoTeamSelect": ("禁止队伍选择", "禁止单位被队伍选择"),
    "NoTeamChange": ("禁止队伍变更", "禁止单位的队伍变更"),
    "NoUnitCollision": ("禁用单位碰撞", "禁用单位间的碰撞"),
    "NotOnMinimap": ("不显示在小地图", "使单位不显示在小地图上"),
    "NotOnMinimapForEnemies": ("对敌方不显示在小地图", "使单位对敌方不显示在小地图上"),
    "NotifyWearablesOfModelChange": ("通知饰品模型变化", "通知饰品单位模型发生变化"),
})

# 第五批 (P-R开头的方法)
TRANSLATIONS.update({
    "PerformAttack": ("执行攻击", "对目标执行一次攻击"),
    "PickupDroppedItem": ("拾取掉落物品", "拾取地上的掉落物品"),
    "PickupRune": ("拾取神符", "拾取神符"),
    "PlayVCD": ("播放VCD", "播放VCD动画"),
    "Purge": ("净化", "净化单位身上的效果"),
    "QueueConcept": ("排队概念", "将概念加入队列"),
    "ReduceMana": ("减少法力值", "减少单位的法力值"),
    "RemoveAbility": ("移除技能", "移除单位的指定技能"),
    "RemoveAbilityByHandle": ("通过句柄移除技能", "通过技能句柄移除技能"),
    "RemoveAbilityFromIndexByName": ("通过索引和名称移除技能", "通过索引和名称移除技能"),
    "RemoveAllModifiers": ("移除所有修饰器", "移除单位身上的所有修饰器"),
    "RemoveAllModifiersOfName": ("移除所有同名修饰器", "移除单位身上所有指定名称的修饰器"),
    "RemoveGesture": ("移除动作", "移除指定的动作"),
    "RemoveHorizontalMotionController": ("移除水平运动控制器", "移除单位的水平运动控制器"),
    "RemoveItem": ("移除物品", "从单位物品栏移除物品"),
    "RemoveModifierByName": ("通过名称移除修饰器", "通过名称移除单位的修饰器"),
    "RemoveModifierByNameAndCaster": ("通过名称和施法者移除修饰器", "通过修饰器名称和施法者移除修饰器"),
    "RemoveNoDraw": ("移除不绘制标志", "移除单位的不绘制标志"),
    "RemoveVerticalMotionController": ("移除垂直运动控制器", "移除单位的垂直运动控制器"),
    "RespawnUnit": ("复活单位", "复活该单位"),
})

# 第六批 (S开头的方法)
TRANSLATIONS.update({
    "Script_GetAttackRange": ("脚本获取攻击距离", "获取单位的攻击距离"),
    "SellItem": ("出售物品", "出售指定物品"),
    "SetAbilityByIndex": ("通过索引设置技能", "在指定索引位置设置技能"),
    "SetAcquisitionRange": ("设置索敌范围", "设置单位的自动索敌范围"),
    "SetAdditionalBattleMusicWeight": ("设置额外战斗音乐权重", "设置单位的额外战斗音乐权重"),
    "SetAggroTarget": ("设置仇恨目标", "设置单位的仇恨目标"),
    "SetAttackCapability": ("设置攻击能力", "设置单位的攻击能力类型"),
    "SetAttacking": ("设置攻击状态", "设置单位的攻击状态"),
    "SetBaseAttackTime": ("设置基础攻击间隔", "设置单位的基础攻击间隔时间"),
    "SetBaseDamageMax": ("设置基础最大伤害", "设置单位的基础最大攻击伤害"),
    "SetBaseDamageMin": ("设置基础最小伤害", "设置单位的基础最小攻击伤害"),
    "SetBaseHealthRegen": ("设置基础生命恢复", "设置单位的基础生命恢复速度"),
    "SetBaseMagicalResistanceValue": ("设置基础魔法抗性", "设置单位的基础魔法抗性值"),
    "SetBaseManaRegen": ("设置基础法力恢复", "设置单位的基础法力恢复速度"),
    "SetBaseMaxHealth": ("设置基础最大生命值", "设置单位的基础最大生命值"),
    "SetBaseMoveSpeed": ("设置基础移动速度", "设置单位的基础移动速度"),
    "SetCanSellItems": ("设置可出售物品", "设置单位是否可以出售物品"),
    "SetControllableByPlayer": ("设置可被玩家控制", "设置单位是否可被指定玩家控制"),
    "SetCursorCastTarget": ("设置光标施法目标", "设置光标指向的施法目标"),
    "SetCursorPosition": ("设置光标位置", "设置光标的位置"),
    "SetCursorTargetingNothing": ("设置光标无目标", "设置光标为无目标状态"),
    "SetCustomHealthLabel": ("设置自定义血条标签", "设置单位的自定义血条标签文本"),
    "SetDayTimeVisionRange": ("设置白天视野范围", "设置单位的白天视野范围"),
    "SetDeathXP": ("设置死亡经验", "设置击杀该单位获得的经验值"),
    "SetForceAttackTarget": ("设置强制攻击目标", "设置单位的强制攻击目标"),
    "SetForceAttackTargetAlly": ("设置强制攻击友军目标", "设置单位的强制攻击友军目标"),
    "SetHasInventory": ("设置是否有物品栏", "设置单位是否拥有物品栏"),
    "SetHealth": ("设置生命值", "设置单位的当前生命值"),
    "SetHealthBarOffsetOverride": ("设置血条偏移覆盖", "设置单位血条的偏移覆盖值"),
    "SetHullRadius": ("设置碰撞半径", "设置单位的碰撞半径"),
    "SetIdleAcquire": ("设置空闲索敌", "设置单位空闲时是否自动索敌"),
    "SetInitialGoalEntity": ("设置初始目标实体", "设置单位的初始目标实体"),
    "SetMana": ("设置法力值", "设置单位的当前法力值"),
    "SetMaxHealth": ("设置最大生命值", "设置单位的最大生命值"),
    "SetMaxMana": ("设置最大法力值", "设置单位的最大法力值"),
    "SetMaximumGoldBounty": ("设置最大金钱奖励", "设置击杀该单位可能获得的最大金钱"),
    "SetMinimumGoldBounty": ("设置最小金钱奖励", "设置击杀该单位可能获得的最小金钱"),
    "SetModifierStackCount": ("设置修饰器层数", "设置指定修饰器的层数"),
    "SetMoveCapability": ("设置移动能力", "设置单位的移动能力类型"),
    "SetMustReachEachGoalEntity": ("设置必须到达每个目标", "设置单位是否必须到达每个目标实体"),
    "SetNeverMoveToClearSpace": ("设置从不移动清空空间", "设置单位从不移动以清空空间"),
    "SetNightTimeVisionRange": ("设置夜间视野范围", "设置单位的夜间视野范围"),
    "SetOrigin": ("设置原点", "设置单位的原点位置"),
    "SetOriginalModel": ("设置原始模型", "设置单位的原始模型"),
    "SetPhysicalArmorBaseValue": ("设置基础物理护甲", "设置单位的基础物理护甲值"),
    "SetRangedProjectileName": ("设置远程弹道名称", "设置单位的远程弹道名称"),
    "SetShouldComputeRemainingPathLength": ("设置是否计算剩余路径", "设置是否计算剩余路径长度"),
    "SetShouldDoFlyHeightVisual": ("设置是否显示飞行高度", "设置是否显示飞行高度视觉效果"),
    "SetStolenScepter": ("设置被偷取的神杖", "设置单位是否拥有被偷取的神杖效果"),
    "SetUnitCanRespawn": ("设置单位可复活", "设置单位是否可以复活"),
    "SetUnitName": ("设置单位名称", "设置单位的内部名称"),
    "ShouldIdleAcquire": ("是否应空闲索敌", "检查单位是否应该在空闲时自动索敌"),
    "SpendMana": ("消耗法力值", "消耗单位的法力值"),
    "StartGesture": ("开始动作", "开始播放指定动作"),
    "StartGestureWithPlaybackRate": ("以播放速率开始动作", "以指定播放速率开始播放动作"),
    "Stop": ("停止", "停止单位当前的动作"),
    "SwapAbilities": ("交换技能", "交换两个技能的位置"),
    "SwapItems": ("交换物品", "交换两个物品的位置"),
})

# 第七批 (T-Z开头的方法)
TRANSLATIONS.update({
    "TakeItem": ("取走物品", "取走指定物品"),
    "TimeUntilNextAttack": ("距下次攻击时间", "获取距离下次攻击的时间"),
    "TriggerModifierDodge": ("触发修饰器闪避", "触发修饰器的闪避效果"),
    "TriggerSpellAbsorb": ("触发法术吸收", "触发法术吸收效果"),
    "TriggerSpellReflect": ("触发法术反射", "触发法术反射效果"),
    "UnitCanRespawn": ("单位是否可复活", "检查单位是否可以复活"),
    "WasKilledPassively": ("是否被动死亡", "检查单位是否被动死亡"),
})

def apply_translations():
    # 读取文件
    with open('data/luaapi/classes_cn.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 找到CDOTA_BaseNPC类
    basenpc_idx = None
    for i, item in enumerate(data['items']):
        if item['name'] == 'CDOTA_BaseNPC':
            basenpc_idx = i
            break
    
    if basenpc_idx is None:
        print("未找到 CDOTA_BaseNPC 类")
        return
    
    # 应用翻译
    methods = data['items'][basenpc_idx]['methods']
    translated_count = 0
    
    for method in methods:
        method_name = method['name']
        if method_name in TRANSLATIONS:
            name_cn, desc_cn = TRANSLATIONS[method_name]
            if not method.get('name_cn') or method['name_cn'].strip() == '':
                method['name_cn'] = name_cn
                method['description_cn'] = desc_cn
                translated_count += 1
    
    # 保存文件
    with open('data/luaapi/classes_cn.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"已翻译 {translated_count} 个方法")
    print(f"翻译字典共有 {len(TRANSLATIONS)} 个条目")
    
    # 检查剩余未翻译的
    untranslated = []
    for m in methods:
        if not m.get('name_cn') or m['name_cn'].strip() == '':
            untranslated.append(m['name'])
    
    print(f"剩余未翻译: {len(untranslated)} 个")
    if untranslated:
        print("未翻译的方法:")
        for name in untranslated[:20]:
            print(f"  - {name}")
        if len(untranslated) > 20:
            print(f"  ... 还有 {len(untranslated) - 20} 个")

if __name__ == '__main__':
    apply_translations()
