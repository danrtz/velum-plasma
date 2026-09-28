// SPDX-License-Identifier: GPL-2.0-or-later
#include <effect/effect.h>
#include <effect/effecthandler.h>
#include <KConfigGroup>
#include <input.h>
#include <input_event.h>
#include <workspace.h>
#include <window.h>
#include <core/output.h>
#include <QChronoTimer>
#include <QElapsedTimer>
#include <QPointer>

namespace KWin {
class ResizeFilter : public QObject, public InputEventFilter
{
    Q_OBJECT
public:
    ResizeFilter() : InputEventFilter(InputFilterOrder::InteractiveMoveResize)
    {
        m_timer.setSingleShot(true);
        m_timer.setTimerType(Qt::PreciseTimer);
        connect(&m_timer, &QChronoTimer::timeout, this, &ResizeFilter::flush);
        input()->installInputEventFilter(this);
    }
    ~ResizeFilter() override { flush(); }
    void setMaxRate(int rate) { m_maxRate = rate > 0 ? std::clamp(rate, 30, 360) : 0; }
    QString debug() const
    {
        return QStringLiteral("resize motions=%1 updates=%2 pending=%3 maxRate=%4")
            .arg(m_motions).arg(m_updates).arg(m_pending).arg(m_maxRate);
    }
    bool pointerMotion(PointerMotionEvent *event) override
    {
        Window *window = workspace()->moveResizeWindow();
        if (!window || !window->isInteractiveResize()) {
            clear();
            return false;
        }
        ++m_motions;
        if (m_window != window) {
            clear();
            m_window = window;
        }
        m_position = event->position;
        m_modifiers = event->modifiers;
        m_pending = true;
        auto refresh = window->output() ? window->output()->refreshRate() : 60000u;
        if (m_maxRate) refresh = std::min(refresh, uint32_t(m_maxRate * 1000));
        const auto interval = std::chrono::nanoseconds(1000000000000LL / std::max(refresh, 1000u));
        const auto elapsed = m_clock.isValid() ? m_clock.durationElapsed() : interval;
        if (elapsed >= interval) {
            flush();
        } else if (!m_timer.isActive()) {
            m_timer.setInterval(interval - elapsed);
            m_timer.start();
        }
        // The pointer has already moved. Only the native resize handler is coalesced.
        return true;
    }
    bool pointerButton(PointerButtonEvent *) override
    {
        flush(); // Deliver the last position before KWin finishes the resize.
        clear();
        return false;
    }
    bool keyboardKey(KeyboardKeyEvent *event) override
    {
        if (event->key == Qt::Key_Escape) clear();
        else flush();
        return false; // Keep KWin's cancel/finish and keyboard-resize handling.
    }
private:
    void clear()
    {
        m_timer.stop();
        m_pending = false;
        m_window.clear();
        m_clock.invalidate();
    }
    void flush()
    {
        m_timer.stop();
        if (!m_pending) return;
        m_pending = false;
        if (!workspace() || !m_window || workspace()->moveResizeWindow() != m_window || !m_window->isInteractiveResize()) {
            clear();
            return;
        }
        m_clock.start();
        ++m_updates;
        m_window->updateInteractiveMoveResize(m_position, m_modifiers);
    }
    QChronoTimer m_timer;
    QElapsedTimer m_clock;
    QPointer<Window> m_window;
    QPointF m_position;
    Qt::KeyboardModifiers m_modifiers;
    int m_maxRate = 0;
    bool m_pending = false;
    quint64 m_motions = 0, m_updates = 0;
};
class ResizePacer : public Effect
{
public:
    ResizePacer() { reconfigure(ReconfigureAll); }
    void reconfigure(ReconfigureFlags) override
    {
        m_filter.setMaxRate(KConfigGroup(effects->config(), "Effect-velum_resize_pacer").readEntry("MaxRate", 0));
    }
    bool isActive() const override { return false; }
    QString debug(const QString &) const override { return m_filter.debug(); }
private:
    ResizeFilter m_filter;
};
KWIN_EFFECT_FACTORY_SUPPORTED_ENABLED(ResizePacer, "metadata.json", return input() && workspace();, return false;)
}
#include "pacer.moc"
