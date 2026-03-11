from pydantic import AliasChoices, BaseModel, Field


class SpinRequest(BaseModel):
    session_token: str = Field(
        ...,
        min_length=1,
        max_length=120,
        validation_alias=AliasChoices("session_token", "session_id"),
    )


class SpinResponse(BaseModel):
    status: str
    session_token: str
    reward_label: str
    reward_code: str | None = None
    reward_status: str


class RewardResponse(BaseModel):
    session_token: str
    reward_label: str
    reward_code: str | None = None
    reward_status: str


class GamesAnalyticsResponse(BaseModel):
    total_spins: int
    unique_sessions: int
    issued_rewards: int
    redeemed_rewards: int
    redemption_rate: float


class RewardRedeemResponse(BaseModel):
    reward_code: str
    reward_status: str


class GameRuleInput(BaseModel):
    label: str = Field(..., min_length=1, max_length=120)
    weight: int = Field(..., ge=0, le=10000)
    redeemable: bool
    is_active: bool = True


class GameSettingsTodayUpdateRequest(BaseModel):
    rules: list[GameRuleInput] = Field(default_factory=list)


class GameRuleResponse(BaseModel):
    label: str
    weight: int
    redeemable: bool
    is_active: bool


class GameSettingsTodayResponse(BaseModel):
    date: str
    rules: list[GameRuleResponse]


class RewardIssuedRow(BaseModel):
    reward_code: str | None = None
    reward_label: str
    reward_status: str
    session_token: str
    table_id: str
    created_at: str


class RewardsTodayResponse(BaseModel):
    date: str
    items: list[RewardIssuedRow]
