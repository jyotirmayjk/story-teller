export function TranscriptPanel({
  partial,
  finalText,
  assistantText,
}: {
  partial: string;
  finalText: string;
  assistantText: string;
}) {
  return (
    <div className="panel stack">
      <div>
        <p className="section-kicker">Transcript</p>
        <p className="body-copy">{partial || finalText || 'Press and hold the mic to start a conversation.'}</p>
      </div>
      <div>
        <p className="section-kicker">Assistant Reply</p>
        <p className="body-copy">{assistantText || 'The assistant response will stream here.'}</p>
      </div>
    </div>
  );
}
