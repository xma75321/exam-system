"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";

interface TrendData {
  date: string;
  score: number;
  exam_title: string;
  pass_score: number;
}

interface TrendChartProps {
  data: TrendData[];
}

export default function TrendChart({ data }: TrendChartProps) {
  if (data.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center rounded-lg bg-gray-50">
        <p className="text-gray-500">暂无考试记录</p>
      </div>
    );
  }

  // 计算及格线（取平均值）
  const avgPassScore =
    data.reduce((sum, d) => sum + d.pass_score, 0) / data.length;

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{
            top: 5,
            right: 30,
            left: 20,
            bottom: 5,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => {
              const date = new Date(value);
              return `${date.getMonth() + 1}/${date.getDate()}`;
            }}
          />
          <YAxis
            domain={[0, 100]}
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => `${value}分`}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload as TrendData;
                return (
                  <div className="rounded-lg border border-gray-200 bg-white p-3 shadow-sm">
                    <p className="text-sm font-medium text-gray-900">
                      {data.exam_title}
                    </p>
                    <p className="mt-1 text-sm text-gray-500">{data.date}</p>
                    <p className="mt-2 text-lg font-semibold text-primary-600">
                      {data.score.toFixed(1)} 分
                    </p>
                    <p className="mt-1 text-xs text-gray-400">
                      及格线: {data.pass_score} 分
                    </p>
                  </div>
                );
              }
              return null;
            }}
          />
          <ReferenceLine
            y={avgPassScore}
            stroke="#ef4444"
            strokeDasharray="5 5"
            label={{
              value: `及格线 ${avgPassScore.toFixed(0)}`,
              position: "right",
              fill: "#ef4444",
              fontSize: 12,
            }}
          />
          <Line
            type="monotone"
            dataKey="score"
            stroke="#6366f1"
            strokeWidth={2}
            dot={{ fill: "#6366f1", strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
