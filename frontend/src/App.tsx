import React, { useState, useRef, useEffect } from 'react';
import { Layout, Input, Button, List, Card, Tag, Typography, Space, Divider, Spin, Alert } from 'antd';
import { SendOutlined, RobotOutlined, UserOutlined, SafetyCertificateOutlined, WarningOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Header, Content, Sider } = Layout;
const { Text, Title, Paragraph } = Typography;
const { TextArea } = Input;

// Types matching Backend
interface IntentAnalysis {
  intent: string;
  confidence: number;
  reasoning: string;
}

interface EmotionRiskAnalysis {
  emotion_level: number;
  risk_tags: string[];
  risk_score: number;
}

interface StrategyDecision {
  strategy: string;
  prompt_template_name: string;
  reasoning: string;
}

interface BotResponse {
  content: string;
  intent_analysis: IntentAnalysis;
  emotion_analysis: EmotionRiskAnalysis;
  strategy_decision: StrategyDecision;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  debugInfo?: BotResponse;
}

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: '您好，欢迎光临[EcomCare商城]，我是您的专属客服。请问有什么想买的或者需要帮助的吗？' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentDebug, setCurrentDebug] = useState<BotResponse | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const userMsg: Message = { role: 'user', content: inputValue };
    setMessages(prev => [...prev, userMsg]);
    setInputValue('');
    setLoading(true);

    try {
      // Build history for context (simplified)
      const history = messages.map(m => ({ role: m.role, content: m.content }));
      
      const response = await axios.post('/api/chat', {
        message: userMsg.content,
        history: history
      });

      const botData: BotResponse = response.data;
      const botMsg: Message = { 
        role: 'assistant', 
        content: botData.content,
        debugInfo: botData
      };

      setMessages(prev => [...prev, botMsg]);
      setCurrentDebug(botData);

    } catch (error) {
      console.error(error);
      const errorMsg: Message = { role: 'assistant', content: '抱歉，系统暂时繁忙，请稍后再试。' };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const getEmotionColor = (level: number) => {
    if (level === 0) return 'green';
    if (level === 1) return 'orange';
    if (level === 2) return 'volcano';
    return 'red';
  };

  return (
    <Layout style={{ height: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', background: '#001529', padding: '0 24px' }}>
        <RobotOutlined style={{ fontSize: '24px', color: '#fff', marginRight: '16px' }} />
        <Title level={3} style={{ color: '#fff', margin: 0 }}>EcomCare 智能客服系统</Title>
        <Tag color="blue" style={{ marginLeft: '20px' }}>电商客服 & 售后处理</Tag>
      </Header>
      <Layout>
        <Content style={{ padding: '20px', display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
          <div style={{ flex: 1, overflowY: 'auto', paddingRight: '10px', marginBottom: '20px' }}>
            <List
              itemLayout="horizontal"
              dataSource={messages}
              renderItem={(item) => (
                <List.Item style={{ border: 'none', padding: '10px 0' }}>
                  <div style={{ 
                    width: '100%', 
                    display: 'flex', 
                    justifyContent: item.role === 'user' ? 'flex-end' : 'flex-start' 
                  }}>
                    <div style={{ 
                      maxWidth: '70%', 
                      display: 'flex', 
                      flexDirection: item.role === 'user' ? 'row-reverse' : 'row',
                      alignItems: 'flex-start'
                    }}>
                      <div style={{ 
                        margin: item.role === 'user' ? '0 0 0 10px' : '0 10px 0 0',
                        background: item.role === 'user' ? '#1890ff' : '#ddd',
                        padding: '8px',
                        borderRadius: '50%',
                        color: '#fff'
                      }}>
                        {item.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                      </div>
                      <Card 
                        bodyStyle={{ padding: '12px' }} 
                        style={{ 
                          background: item.role === 'user' ? '#e6f7ff' : '#fff',
                          borderColor: item.role === 'user' ? '#91d5ff' : '#f0f0f0'
                        }}
                        onClick={() => item.debugInfo && setCurrentDebug(item.debugInfo)}
                        hoverable={!!item.debugInfo}
                      >
                        <Text>{item.content}</Text>
                      </Card>
                    </div>
                  </div>
                </List.Item>
              )}
            />
            <div ref={messagesEndRef} />
          </div>
          <div style={{ background: '#fff', padding: '20px', borderRadius: '8px' }}>
            <Space.Compact style={{ width: '100%' }}>
              <TextArea 
                value={inputValue}
                onChange={e => setInputValue(e.target.value)}
                onPressEnter={(e) => {
                    if(!e.shiftKey) {
                        e.preventDefault();
                        handleSend();
                    }
                }}
                placeholder="请输入您的投诉或咨询内容..."
                autoSize={{ minRows: 1, maxRows: 4 }}
              />
              <Button type="primary" icon={<SendOutlined />} onClick={handleSend} loading={loading} style={{ height: 'auto' }}>
                发送
              </Button>
            </Space.Compact>
          </div>
        </Content>
        <Sider width={400} theme="light" style={{ borderLeft: '1px solid #f0f0f0', padding: '20px', overflowY: 'auto' }}>
          <Title level={4}>系统分析面板</Title>
          <Paragraph type="secondary">点击机器人回复查看详细分析数据。</Paragraph>
          
          {currentDebug ? (
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              
              {/* Intent Section */}
              <Card size="small" title="1. 意图识别 (Intent Detection)">
                <Tag color="blue" style={{ fontSize: '16px', padding: '5px 10px' }}>
                  {currentDebug.intent_analysis.intent}
                </Tag>
                <div style={{ marginTop: '10px' }}>
                  <Text strong>置信度: </Text>
                  <Text>{currentDebug.intent_analysis.confidence}</Text>
                </div>
                <div style={{ marginTop: '5px' }}>
                  <Text type="secondary">{currentDebug.intent_analysis.reasoning}</Text>
                </div>
              </Card>

              {/* Emotion & Risk Section */}
              <Card size="small" title="2. 情绪与风险评估 (Emotion & Risk)">
                <div style={{ marginBottom: '10px' }}>
                    <Text strong>情绪等级: </Text>
                    <Tag color={getEmotionColor(currentDebug.emotion_analysis.emotion_level)}>
                        {currentDebug.emotion_analysis.emotion_level} / 3
                    </Tag>
                </div>
                <div style={{ marginBottom: '10px' }}>
                    <Text strong>风险评分: </Text>
                    <Text type={currentDebug.emotion_analysis.risk_score > 50 ? 'danger' : 'success'}>
                        {currentDebug.emotion_analysis.risk_score}
                    </Text>
                </div>
                <div>
                    <Text strong>风险标签: </Text>
                    {currentDebug.emotion_analysis.risk_tags.length > 0 ? (
                        currentDebug.emotion_analysis.risk_tags.map(tag => (
                            <Tag color="red" key={tag}>{tag}</Tag>
                        ))
                    ) : <Text type="secondary">无</Text>}
                </div>
              </Card>

              {/* Strategy Section */}
              <Card size="small" title="3. 策略路由 (Strategy Routing)">
                <Tag color="purple" style={{ fontSize: '16px', padding: '5px 10px', marginBottom: '10px', display: 'block', textAlign: 'center' }}>
                    {currentDebug.strategy_decision.strategy}
                </Tag>
                <Text strong>Prompt 模板: </Text> <Text code>{currentDebug.strategy_decision.prompt_template_name}</Text>
                <Divider style={{ margin: '10px 0' }} />
                <Text type="secondary">{currentDebug.strategy_decision.reasoning}</Text>
              </Card>

              {/* Action Suggestion */}
               {currentDebug.strategy_decision.strategy === '升级人工' && (
                   <Alert
                    message="触发人工升级"
                    description="当前对话已被标记，建议人工立即介入处理。"
                    type="warning"
                    showIcon
                    icon={<WarningOutlined />}
                   />
               )}
            </Space>
          ) : (
            <div style={{ textAlign: 'center', marginTop: '50px', color: '#ccc' }}>
                <RobotOutlined style={{ fontSize: '48px' }} />
                <p>暂无分析数据</p>
            </div>
          )}
        </Sider>
      </Layout>
    </Layout>
  );
};

export default App;
